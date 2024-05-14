class AnalysisInfoMsg(object):

    def __init__(self, step, status, msg=None):

        # 步骤状态
        # 0-开始，1-正常结束，2-手动停止，3-步骤执行异常, 9-仅仅只是消息， 10-开始一个msconvert，11-完成一个msconvert，20-开始一个diann， 21-完成一个diann处理， 99-整体流程结束
        self.status = status

        """
        步骤：
            1-初始化数据
            2-msconvert
            3-diann
            4-build mzml info
            5-S3
            6-S4
            7-S5
            8-S6
            9-save data
            10-ai pred
            11-draw pic
            12-save pred csv
            13-clear mzml
        """
        self.step = step
        self.msg = msg

