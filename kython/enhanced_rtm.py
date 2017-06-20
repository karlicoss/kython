from rtmapi import Rtm # type: ignore


class EnhancedRtm:
    def __init__(self, api_key: str, api_secret: str, token: str) -> None:
        self.api = Rtm(api_key, api_secret, token=token)
        self.timeline = self.api.rtm.timelines.create().timeline.value
        # TODO check for errors

    def addTask(self, description: str, parent_id: str=None) -> str:
        """
           returns id of the new task
        """
        params = {
            'name'    : description,
            'timeline': self.timeline,
            'parse'   : '1',
        }
        if parent_id is not None:
            params['parent_task_id'] = parent_id
        res = self.api.rtm.tasks.add(**params)
        return res.list.taskseries.task.id
