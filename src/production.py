import pandas as pd
import datetime
import calendar
import holidays

PROCESS_NAMES = ["사출", "경화", "냉각", "탈형/조립", "건조", "외주가공", "마무리(그라인딩, 차폐몰딩 등, 세척/포장)"]

def check_if_working_day(date_time, working_time_min, working_time_max,
                         work_on_saturday=False, work_on_sunday=False,
                         work_on_holiday=False, three_day_shift=False):
    """
    작업일인지 확인
    
    Parameters
    ----------
    date_time         : datetime (datetime.datetime(2022, 8, 18, 9, 0))
                        날짜
                    
    work_on_saturday  : boolean
                        토요일 근무 여부
    
    work_on_sunday    : boolean
                        일요일 근무 여부
    
    work_on_holiday   : boolean
                        공휴일 근무 여부
    
    three_day_shift   : boolean
                        잠 안자고 네버스탑???
                        (this option overwrite other parameters)

    Returns
    -------
    작업일 여부 : boolean

    Examples
    --------
    >>> check_if_working_day(datetime.datetime(2022, 8, 18, 9, 0),
            work_on_saturday=False, work_on_sunday=False,
            work_on_holiday=False, three_day_shift=False)
    """
    if three_day_shift == True:
        return True
    else:
        if work_on_saturday == True and work_on_sunday == True and work_on_holiday == True:
            if working_time_min <= date_time.hour <= working_time_max:
                return True
            else:
                return False
        elif work_on_saturday == True and work_on_sunday == True and work_on_holiday == False:
            if date_time not in holidays.KR():
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False
        elif work_on_saturday == True and work_on_sunday == False and work_on_holiday ==True:
            if date_time.weekday() < 6:
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False
        elif work_on_saturday == True and work_on_sunday == False and work_on_holiday == False:
            if date_time.weekday() < 6 and date_time not in holidays.KR():
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False 
        elif work_on_saturday == False and work_on_sunday == True and work_on_holiday == True:
            if date_time.weekday() < 5 or date_time.weekday() == 6:
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False 
        elif work_on_saturday == False and work_on_sunday == True and work_on_holiday == False:
            if (date_time.weekday() < 5 or date_time.weekday() == 6) and date_time not in holidays.KR():
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False
        elif work_on_saturday == False and work_on_sunday == False and work_on_holiday == True:
            if date_time.weekday() < 5:
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False
        else:
            if date_time.weekday() < 5 and date_time not in holidays.KR():
                if working_time_min <= date_time.hour <= working_time_max:
                    return True
                else:
                    return False
            else:
                return False


def calculate_production_time(
    num_joints, start_time, injection_time, curing_time, cooling_time, mold_reset_time,
    mold_preheating_time, drying_time, outsourcing_time, final_touch_time,
    working_time_min, working_time_max,
    work_on_saturday=False, work_on_sunday=False, work_on_holiday=False, three_day_shift=False,
):
    """
    접속재 제조 소요일 계산
    
    Parameters
    ----------
    num_joints    : int
                    접속재 필요 수량
    
    start_time     : datetime (datetime.datetime(2022, 8, 18, 9, 0))
                     작업 시작 시간

    work_on_saturday  : boolean
                        토요일 근무 여부
    
    work_on_sunday    : boolean
                        일요일 근무 여부
    
    work_on_holiday   : boolean
                        공휴일 근무 여부
    
    three_day_shift   : boolean
                        잠 안자고 네버스탑???
                        (this option overwrite other parameters)

    Returns
    -------
    접속재 제조 소요일 : dataframe

    Examples
    --------
    >>> calculate_production_time(5, datetime.datetime(2022, 8, 18, 9, 0),
            work_on_saturday=False, work_on_sunday=False,
            work_on_holiday=False, three_day_shift=False)
    """
    # Initialization of list for times
    start = []
    finish = []
    
    num_joint = 0
    
    time = start_time
    
    while num_joint < num_joints:
        if check_if_working_day(
            time, working_time_min, working_time_max, work_on_saturday, 
            work_on_sunday, work_on_holiday, three_day_shift
            ):
            start.append(time)
            time = time + injection_time
            finish.append(time)
            start.append(time)
            time = time + curing_time
            finish.append(time)
            start.append(time)
            time = time + cooling_time
            finish.append(time)
            
            if check_if_working_day(
                time, working_time_min, working_time_max, work_on_saturday, 
                work_on_sunday, work_on_holiday, three_day_shift
                ):
                start.append(time)
                time = time + mold_reset_time
                finish.append(time)
                start.append(time)              # 건조 시간 추가
                time_2 = time + drying_time     # 건조 시간 추가
                finish.append(time_2)           # 건조 시간 추가
                if check_if_working_day(
                    time_2, working_time_min, working_time_max, work_on_saturday, 
                    work_on_sunday, work_on_holiday, three_day_shift
                    ):
                    start.append(time_2)                   # 외주 가공 시간 추가
                    time_2 = time_2 + outsourcing_time     # 외주 가공 시간 추가
                    time_2 = time_2.replace(hour=10)      # 외주 가공 시간 추가
                    finish.append(time_2)                  # 외주 가공 시간 추가
                    if check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ):
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                    else:
                        while check_if_working_day(
                            time_2, working_time_min, working_time_max, work_on_saturday, 
                            work_on_sunday, work_on_holiday, three_day_shift
                            ) == False:
                            time_2 = time_2 + datetime.timedelta(hours=1)
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                else:
                    while check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ) == False:
                        time_2 = time_2 + datetime.timedelta(hours=1)
                    start.append(time_2)                   # 외주 가공 시간 추가
                    time_2 = time_2 + outsourcing_time     # 외주 가공 시간 추가
                    time_2 = time_2.replace(hour=10)      # 외주 가공 시간 추가
                    finish.append(time_2)                  # 외주 가공 시간 추가
                    if check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ):
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                    else:
                        while check_if_working_day(
                            time_2, working_time_min, working_time_max, work_on_saturday, 
                            work_on_sunday, work_on_holiday, three_day_shift
                            ) == False:
                            time_2 = time_2 + datetime.timedelta(hours=1)
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time

            else:
                while check_if_working_day(
                    time, working_time_min, working_time_max, work_on_saturday, 
                    work_on_sunday, work_on_holiday, three_day_shift
                    ) == False:
                    time = time + datetime.timedelta(hours=1)
                start.append(time)
                time = time + mold_reset_time
                finish.append(time)
                start.append(time)                # 건조 시간 추가
                time_2 = time + drying_time     # 건조 시간 추가
                finish.append(time_2)           # 건조 시간 추가
                if check_if_working_day(
                    time_2, working_time_min, working_time_max, work_on_saturday, 
                    work_on_sunday, work_on_holiday, three_day_shift
                    ):
                    start.append(time_2)                   # 외주 가공 시간 추가
                    time_2 = time_2 + outsourcing_time     # 외주 가공 시간 추가
                    time_2 = time_2.replace(hour=10)      # 외주 가공 시간 추가
                    finish.append(time_2)                  # 외주 가공 시간 추가
                    if check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ):
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                    else:
                        while check_if_working_day(
                            time_2, working_time_min, working_time_max, work_on_saturday, 
                            work_on_sunday, work_on_holiday, three_day_shift
                            ) == False:
                            time_2 = time_2 + datetime.timedelta(hours=1)
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                else:
                    while check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ) == False:
                        time_2 = time_2 + datetime.timedelta(hours=1)
                    start.append(time_2)                   # 외주 가공 시간 추가
                    time_2 = time_2 + outsourcing_time     # 외주 가공 시간 추가
                    time_2 = time_2.replace(hour=10)      # 외주 가공 시간 추가
                    finish.append(time_2)                  # 외주 가공 시간 추가
                    if check_if_working_day(
                        time_2, working_time_min, working_time_max, work_on_saturday, 
                        work_on_sunday, work_on_holiday, three_day_shift
                        ):
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
                    else:
                        while check_if_working_day(
                            time_2, working_time_min, working_time_max, work_on_saturday, 
                            work_on_sunday, work_on_holiday, three_day_shift
                            ) == False:
                            time_2 = time_2 + datetime.timedelta(hours=1)
                        start.append(time_2)                    # 마무리 시간 추가
                        time_2 = time_2 + final_touch_time      # 마무리 시간 추가
                        finish.append(time_2)                   # 마무리 시간 추가
                        num_joint += 1
                        time = time + mold_preheating_time
            
        else:
            while check_if_working_day(
                time, working_time_min, working_time_max, work_on_saturday, 
                work_on_sunday, work_on_holiday, three_day_shift
                ) == False:
                time = time + datetime.timedelta(hours=1)
    
    col_names = ["Number", "Process", "Start", "Finish"]
    process_names = [f"{PROCESS_NAMES[j]}_{i+1}" for i in range(num_joints) for j in range(len(PROCESS_NAMES)) ]
    numbers = [str(i+1) for i in range(num_joints) for j in range(len(PROCESS_NAMES))]

    df = pd.DataFrame(index=range(len(process_names)), columns=col_names)
    
    df["Number"] = numbers
    df["Process"] = process_names
    df["Start"] = start
    df["Finish"] = finish

    return df
