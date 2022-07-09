class Error_log:
    errorlog_id = None
    errorlog_date = None
    errorlog_data = None
    errorlog_labeled_id = None
    def __init__(self,p_errorlog_id,p_errorlog_date,p_errorlog_data,p_errorlog_labeled_id):
        self.errorlog_id = p_errorlog_id
        self.errorlog_date = p_errorlog_date
        self.errorlog_data = p_errorlog_data
        self.errorlog_labeled_id = p_errorlog_labeled_id


