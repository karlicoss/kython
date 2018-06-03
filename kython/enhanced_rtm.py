from .misc import chunks
# pylint: disable=import-error
from rtmapi import Rtm # type: ignore


class EnhancedRtm:
    def __init__(self, api_key: str, api_secret: str, token: str) -> None:
        self.api = Rtm(api_key, api_secret, token=token)
        self.timeline = self.api.rtm.timelines.create().timeline.value
        # TODO check for errors

    # rtm doesn't have a syntax for exact match, what a shame!
    def getTaskByName(self, name: str):
        res = self.api.rtm.tasks.getList(filter=f'name:"{name}"')
        [tlist] = list(res.tasks)
        tname = [t for t in tlist if t.name == name]
        # TODO weird... but looks necessary if you were messing with repetition at some point
        task = max(tname, key=lambda t: t.modified)
        return task

    def addTask_(self, description: str, parent_id: str=None):
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
        return res

    def addTask(self, description: str, parent_id: str=None) -> str:
        return self.addTask_(description, parent_id=parent_id).list.taskseries.task.id

    # since RTM api uses GET requests (and apparently, POST is broken)
    # if your note is too long, the requests will fail :(
    # enable long_note_hack to split it into multiple notes
    def addNote(self, task, text: str, title="", long_note_hack=False):
        if long_note_hack:
            # reversed so they appear in order in RTM
            for ch in reversed(list(chunks(text, 700))): # 700 is kinda made up..
                self.addNote(task, ch, title=title, long_note_hack=False)
            return
        lid = task.list.id
        tsid = task.list.taskseries.id
        tid = task.list.taskseries.task.id
        return self.api.rtm.tasks.notes.add(
            timeline=self.timeline,
            list_id=lid,
            task_id=tid,
            taskseries_id=tsid,
            note_text=text,
            note_title=title,
        )


