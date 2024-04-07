class WorkflowSelector(object):

    def __init__(self, max_workers=4):
        self.max_workers = max_workers

    def select(self, running, idle):
        task_number = max(0, self.max_workers - len(running))
        return list(idle)[:task_number]
