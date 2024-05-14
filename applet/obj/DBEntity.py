class InstInfo(object):

    def __init__(self, ms_inst_id=None, ms_model=None):
        self.id = None
        self.ms_inst_id = ms_inst_id
        self.ms_model = ms_model

    def get_key_val(self):
        return [self.ms_inst_id,
                self.ms_model]


class RunInfo(object):
    def __init__(self, inst_name=None, run_prefix=None, run_id=None, run_name=None, file_name=None, file_type=None,
                 source=None, state=0, is_delete=0,
                 seq_id=None):
        self.id = None
        self.inst_name = inst_name
        self.run_prefix = run_prefix
        self.run_id = run_id
        self.run_name = run_name
        self.file_name = file_name
        self.file_type = file_type
        self.seq_id = seq_id
        self.state = state

        self.last_modify_time = None
        self.file_size = None
        self.source = source
        self.is_delete = is_delete
        self.gmt_create = None

    def get_key_val(self):
        return (self.inst_name, self.run_prefix, self.run_id, self.run_name,
                self.file_name, self.file_type, self.seq_id, self.state, self.last_modify_time, self.file_size,
                self.source,
                self.is_delete)


class RunData(object):
    def __init__(self, seq_id=None, data_tag=None, data_val=None):
        self.id = None
        self.seq_id = seq_id
        self.data_tag = data_tag
        self.data_val = data_val

    def get_key_val(self):
        return (self.seq_id, self.data_tag,
                self.data_val)


class RunDataF4(object):
    def __init__(self, seq_id=None, data_index=None, data_val=None):
        self.id = None
        self.seq_id = seq_id
        self.data_index = data_index
        self.data_val = data_val

    def get_key_val(self):
        return (self.seq_id, self.data_index,
                self.data_val)


class RunDataS7(object):
    def __init__(self, seq_id=None, data_tag=None, pept=None, data_val=None):
        self.id = None
        self.seq_id = seq_id
        self.data_tag = data_tag
        self.pept = pept
        self.data_val = data_val

    def get_key_val(self):
        return (self.seq_id, self.data_tag, self.pept,
                self.data_val)


class PredInfo(object):
    def __init__(self, run_id=None, seq_id=None, pred_key=None, pred_score=None, pred_label=None):
        self.id = None
        self.run_id = run_id
        self.seq_id = seq_id
        self.pred_key = pred_key
        self.pred_score = pred_score
        self.pred_label = pred_label

    def get_key_val(self):
        return (self.run_id, self.seq_id, self.pred_key, self.pred_score,
                self.pred_label)
