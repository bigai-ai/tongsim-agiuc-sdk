# 📷 Camera

Camera 是 TongSim 中模拟视觉感知能力的核心组件。它提供一套用于同步/非同步获取图像数据的接口，包括 RGB 图像、深度图、分割图、镜子中的分割图，以及可见物体列表等。

[API 参考](../api/ability_camera.md)

## 流式通信 & 基准频率说明

Camera 图像通信基于 gRPC Stream 实现。你可以通过调用 `start_imagedata_streaming()` 启动图像数据流接收，在后台持续获取来自 Unreal 场景的图像帧。

Unreal 渲染图像代价较高，因此建议控制取图频率，避免资源浪费。客户端频繁请求不会带来更高的刷新速率，反而可能反复获取同一帧图像。

!!! info "最高刷新频率"
    图像刷新存在服务器侧的基准频率。如果客户端请求频率超过该基准频率，最终将会频繁接收到重复图像帧。

## 分割图 & 分割 ID 管理

分割图的获取依赖 PG 系统运行。

- 启动 `pg_manager.start_pg_stream()` 后，TongSim 会自动为每个物体分配唯一的分割图 ID
- 图像中的每个像素颜色值编码为 4 通道，代表一个 `uint32_t` 类型的对象 ID
- 可在 PG 查询中获取对应物体的分割 ID

```
分割图像素 → 分割 ID 的转换公式：
    id = R + G * 256 + B * 256² + A * 256³
```

!!! info "PG 依赖提醒"
    分割图中每个像素的对象归属依赖 PG 中的分割 ID 设定。未设置 PG 流时，分割图像素无语义意义。

## 深度图压缩与解压

为了节省传输带宽，相机获取到的深度图是经过压缩处理的。

!!! tip "深度图解压"
    解压后每个像素点单位为 cm，以下为示例处理方法：

    ```python
    def hdr_2_npy(self, binary_data, from_eye=False):
        data = imageio.imread(binary_data)
        h_, w_ = data.shape[:2]
        red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2]
        tmp2 = np.hstack((red, green, blue)).reshape(h_ * 3, w_)
        zero_index = np.where(tmp2 == 0)
        tmp2[zero_index] = 1 / 10000
        depth = 10 / (tmp2 * 0.09998)

        if from_eye:
            depth = depth.reshape((h_ * 3, w_))
            depth = depth.T
            depth = np.flip(depth, axis=1)
        depth = depth.reshape((h_ * 3, w_, 1))
        depth = depth[0:-1, :, :]
        return depth
    ```

## 精确的可见性结果

Camera 组件支持返回当前帧中图像“真正看得见”的所有对象列表。这在未集成真实 CV 感知模块时，可用于模拟智能体感知。

!!! info "Visible Object List"
    该列表模拟“图像中每一个出现在可视范围内的物体”。只要物体在图中占据了任意一个像素，就会被加入该列表。

## 多智能体

多智能体场景下若开启多个相机进行图像输出，Unreal 侧负载将显著上升。

!!! info "分布式推荐"
    若需要大规模并发取图（如：20 个相机同时输出 10FPS 图像），建议启用 TongSim 提供的分布式视觉支持，将图像渲染任务分摊至多个服务节点。
