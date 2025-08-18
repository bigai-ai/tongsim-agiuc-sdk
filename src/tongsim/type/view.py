from enum import IntEnum


class ViewModeType(IntEnum):
    """
    摄像机视角模式，用于控制摄像机视角和移动方式。

    Attributes:
        FIRST_PERSON_VIEW (int): 第一人称视角，跟随对象视角。
        SURVEILLANCE_VIEW (int): 监视器视角，用于静态监控场景中的特定区域。
        THIRD_PERSON_VIEW (int): 第三人称视角，跟随对象但保持一定距离。
        ANCHOR_VIEW (int): 锚定在固定位置的视角，没有任何自动化控制逻辑，可通过外部接口设定位姿。
        MANUAL_CONTROL_VIEW (int): 自由相机视角，可以通过 WASD、空格、Ctrl 等键位控制移动。
        TONG_RECON_NAISSANCE_VIEW (int): TongRecon 项目定制化视角模式，用于特殊侦察任务。
        FACE_TO_FACE_VIEW (int): 和智能体面对面相机的视角。
    """

    FIRST_PERSON_VIEW = 0
    SURVEILLANCE_VIEW = 1
    THIRD_PERSON_VIEW = 2
    ANCHOR_VIEW = 3
    MANUAL_CONTROL_VIEW = 4
    TONG_RECON_NAISSANCE_VIEW = 5
    FACE_TO_FACE_VIEW = 6
