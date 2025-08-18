"""
image_data_streaming.pyw

示例：TongSim 相机图像流可视化（支持 RGB / Depth / Segmentation）。

运行方式：
    uv run --with pillow,pygame,numpy,opencv-python ./examples/image/image_data_streaming.pyw

依赖：
    - pillow：图像处理
    - pygame：图形界面
    - numpy：矩阵处理
    - opencv-python：HDR 解码

功能：
    - 启动 Agent + 两个 Camera（first & third person）
    - 获取图像流并可视化
    - 支持按键切换相机和图像类型
        - 按 F 切换摄像头（first/third）
        - 按 T 切换图像类型（RGB / Depth / Seg）
"""

import io
import numpy as np
import pygame
import cv2
from PIL import Image

import tongsim as ts


def hdr_2_npy(binary_data: bytes) -> np.ndarray:
    """
    将 HDR 二进制深度图转换为 (H*3, W) 的浮点深度图（单位 cm）
    RGB 表示图像高度方向的连续三个像素点
    """
    np_buf = np.frombuffer(binary_data, dtype=np.uint8)
    img = cv2.imdecode(np_buf, cv2.IMREAD_UNCHANGED)  # (H, W, 3) float32

    if img is None:
        raise RuntimeError("Failed to decode HDR image with OpenCV.")
    if img.shape[2] != 3:
        raise ValueError(f"Expected HDR image with 3 channels, got shape {img.shape}")

    # 将 (H, W, 3) 拆成三张 (H, W)，再沿 height 拼接为 (H*3, W)
    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = img[:, :, 2]

    # 按行方向堆叠（stack vertically）
    depth_stacked = np.vstack([red, green, blue])  # (H*3, W)

    depth_stacked[depth_stacked == 0] = 1 / 10000
    depth = 10 / (depth_stacked * 0.09998)

    return depth



def visualize_depth(depth: np.ndarray) -> Image.Image:
    """
    将深度图数组映射为可视化图像（灰度图）。

    Args:
        depth (np.ndarray): 深度数组（单位 cm）

    Returns:
        Image.Image: Pillow 图像（8-bit 灰度）
    """
    h = depth.shape[0] // 3
    depth = depth[h:2*h]  # 取中间1/3部分作为代表

    clipped = np.clip(depth, 10, 2000)
    norm = (clipped - clipped.min()) / (clipped.max() - clipped.min())
    img = (255.0 * (1.0 - norm)).astype(np.uint8)
    return Image.fromarray(img, mode="L")


def run_example():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("TongSim Camera Streaming")

    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        ue.open_level("Game_0001")
        agent = ue.spawn_agent("SDBP_Aich_Robot", ts.Vector3(0.0, -300.0, 80.0))

        third_person = ue.spawn_camera("third", ts.Vector3(200, 200, 80), ts.Quaternion())
        third_person.attach_to_target_socket(agent.id, "None")

        first_person = ue.spawn_camera("first", ts.Vector3(0, 0, 80), ts.Quaternion())
        first_person.attach_to_target_socket(agent.id, "InnerMidCameraSocket")

        ue.pg_manager.start_pg_stream(assign_segmentation_id=True)
        third_person.start_imagedata_streaming(True, True, True, False, False)
        first_person.start_imagedata_streaming(True, True, True, False, False)

        # 视角与图像类型切换
        cameras = {"first": first_person, "third": third_person}
        camera_mode = "third"
        image_mode = "seg"

        print("[Hotkeys] F = Switch Camera | T = Switch Image Type")

        # Agent 动作
        for _ in range(6):
            agent.enqueue_action(ts.action.MoveToLocation(ts.Vector3(300, 300, 0)))
            agent.enqueue_action(ts.action.MoveToLocation(ts.Vector3(-300, -300, 0)))
        agent.do_action()

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        camera_mode = "first" if camera_mode == "third" else "third"
                        print(f"[Camera] Switched to: {camera_mode}")
                    elif event.key == pygame.K_t:
                        image_mode = {
                            "rgb": "depth",
                            "depth": "seg",
                            "seg": "rgb"
                        }[image_mode]
                        print(f"[Image] Switched to: {image_mode}")

            camera = cameras[camera_mode]

            try:
                if image_mode == "rgb":
                    buffer = camera.fetch_rgb_from_streaming()
                    if buffer:
                        img = Image.open(io.BytesIO(buffer)).convert("RGB")
                elif image_mode == "depth":
                    buffer = camera.fetch_depth_from_streaming().tobytes()
                    if buffer:
                        depth = hdr_2_npy(buffer)
                        img = visualize_depth(depth).convert("RGB")
                elif image_mode == "seg":
                    buffer = camera.fetch_segmentation_from_streaming()
                    if buffer:
                        img = Image.open(io.BytesIO(buffer)).convert("RGB")
                else:
                    img = None

                if img:
                    img = img.resize((640, 480))
                    surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
                    screen.blit(surface, (0, 0))
                    pygame.display.flip()

            except Exception as e:
                print(f"[Warning] Failed to render image: {e}")

            clock.tick(5)  # FPS 限制

    pygame.quit()


if __name__ == "__main__":
    run_example()
