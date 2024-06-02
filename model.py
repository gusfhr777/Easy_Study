import pickle

COURSE_LIST_FILENAME = 'courseData.pickle'
UNWATCHED_VIDEO_FILENAME = 'unwatchedData.pickle'

class Activity:
    def __init__(self, title: str, link: str, datefrom:str, dateto:str):
        self.title = title
        self.link = link
        self.datefrom = datefrom
        self.dateto = dateto

    def __repr__(self):
        return self.title

class VideoActivity(Activity):
    def __init__(self, title: str, link: str, datefrom:str, dateto:str, video_length=None, isWatched=None):
        super().__init__(title, link, datefrom, dateto)
        self.video_length = video_length
        self.isWatched = isWatched

class FileActivity(Activity):
    def __init__(self, title: str, link: str, datefrom: str, dateto: str, file_size: str,
                 file_type=None):
        super().__init__(title, link, datefrom, dateto)
        self.file_size = file_size
        self.file_type = file_type

class AssignmentActivity(Activity):
    def __init__(self, title: str, link: str, datefrom: str, dateto: str):
        super().__init__(title, link, datefrom, dateto)




class Course:
    course_list = []
    unwatched_video_list = []
    def __init__(self, title: str, professor: str, link: str, course_label: str, course_label_under: str):
        self.title = title
        self.professor = professor
        self.link = link
        self.course_label = course_label
        self.course_label_under = course_label_under
        self.week_list = []

        Course.course_list.append(self)

    def __repr__(self):
        return self.title

    def getActivityList(self, activity_type):
        activity_list = []
        for week in self.week_list:
            for activity in week.activity_list:
                if isinstance(activity, activity_type):
                    activity_list.append(activity)
        return activity_list

    @staticmethod
    def getAllActivityList(activity_type):
        activity_list = []
        for course in Course.course_list:
            for week in course.week_list:
                for activity in week.activity_list:
                    if isinstance(activity, activity_type):
                        activity_list.append(activity)
        return activity_list

    @staticmethod
    def countAllAcivity(activity_type):
        activity_count = 0
        for course in Course.course_list:
            activity_count += len(course.getActivityList(activity_type))
        return activity_count

    @staticmethod
    def printCourse():
        print('현재 수강중인 강의 목록')
        for course in Course.course_list:
            print(f'''강의명 {course.title}
교수 {course.professor}
링크 {course.link}
강의 구분 {course.course_label}
교과여부 {course.course_label_under}
''')
            for week in course.week_list:
                print(f'''{week.title}
요약 : {week.summary}''')
                for activity in week.activity_list:
                    print(f'{activity.title} | 링크 : {activity.link} | 기간 : {activity.datefrom} ~ {activity.dateto}')
                print()
            print('\n----------------------------------\n')

    @staticmethod
    def save():
        with open(COURSE_LIST_FILENAME, 'wb') as f:
            pickle.dump(Course.course_list, f)
        with open(UNWATCHED_VIDEO_FILENAME, 'wb') as f:
            pickle.dump(Course.unwatched_video_list, f)
        print('데이터 저장완료')

    @staticmethod
    def load():
        try:
            with open(COURSE_LIST_FILENAME, 'rb') as f:
                Course.course_list = pickle.load(f)

            with open(UNWATCHED_VIDEO_FILENAME, 'rb') as f:
                Course.unwatched_video_list = pickle.load(f)
        except:
            with open(COURSE_LIST_FILENAME, 'wb'):pass
            with open(UNWATCHED_VIDEO_FILENAME, 'wb'):pass
        print('데이터 불러오기 완료')


class WeekSection:
    def __init__(self, title: str, summary: str, week: int):
        self.title = title
        self.summary = summary
        self.week = week
        self.activity_list = []

    def __repr__(self):
        return self.title

