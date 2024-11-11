class AnalysisInfoMsg(object):

    def __init__(self, step, status, msg=None):

        self.status = status

        """
        
            1-init
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

