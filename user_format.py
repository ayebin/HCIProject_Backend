def basic_format(basic):
    if basic['decide_place']:
        if basic['decide_date']:
            format = f'''
            {basic['age']} {basic['gender']} {basic['num']}이 {basic['place']}으로 {basic['type']}을 가려고 합니다.
            {basic['date_start']}부터 {basic['date_end']}까지 여행을 할 예정입니다.
            여행의 목적은 {basic['purpose']}입니다.
            교통수단은 {basic['transport']}입니다.
            예산은 {basic['budget']}입니다.
            '''
        else:
            format = f'''
            {basic['age']} {basic['gender']} {basic['num']}이 {basic['place']}으로 {basic['type']}을 가려고 합니다.
            여행 기간은 정하지 못하였으나, 대략 {basic['span_approx']}에 {basic['span_month']}개월 {basic['span_week']}주 {basic['span_day']}일 정도 여행할 예정입니다.
            여행의 목적은 {basic['purpose']}입니다.
            교통수단은 {basic['transport']}입니다.
            예산은 {basic['budget']}입니다.
            '''

    else:
        if basic['span_month'] is None:
            basic['span_month'] = 0
        if basic['span_week'] is None:
            basic['span_week'] = 0
        if basic['span_day'] is None:
            basic['span_day'] = 0

        if basic['decide_date']:
            format = f'''
            {basic['age']} {basic['gender']} {basic['num']}이 {basic['type']}을 가려고 합니다.
            {basic['date_start']}부터 {basic['date_end']}까지 여행을 할 예정입니다.
            여행의 목적은 {basic['purpose']}입니다.
            교통수단은 {basic['transport']}입니다.
            예산은 {basic['budget']}입니다.
            여행지를 정하지 못하였기 때문에 추천을 해주세요.
            '''
        else:
            format = f'''
            {basic['age']} {basic['gender']} {basic['num']}이 {basic['type']}을 가려고 합니다.
            여행 기간은 정하지 못하였으나, 대략 {basic['span_approx']}에 {basic['span_month']}개월 {basic['span_week']}주 {basic['span_day']}일 정도 여행할 예정입니다.
            여행의 목적은 {basic['purpose']}입니다.
            교통수단은 {basic['transport']}입니다.
            예산은 {basic['budget']}입니다.
            여행지를 정하지 못하였기 때문에 추천을 해주세요.
            '''
    return format

def detail_format(detail):
    detail_list = []

    if detail['detail_purpose'] is not None:
        detail_purpose = f"구체적인 여행 목표는 다음과 같습니다: {detail['detail_purpose']}"
        detail_list.append(detail_purpose)

    if detail['interest'] is not None:
        interest = f"제 취미 또는 관심사는 다음과 같습니다: {detail['interest']}"
        detail_list.append(interest)

    if detail['special_place'] is not None:
        special_place = f"특별히 가보고 싶은 곳은 다음과 같습니다: {detail['special_place']}"
        detail_list.append(special_place)

    if detail['religion'] is not None:
        religion = f"제 종교는 다음과 같으니 유의해서 여행계획을 만들어주세요: {detail['religion']}"
        detail_list.append(religion)

    if detail['consideration'] is not None:
        consideration = f"추가적으로 다음 사항을 고려해주세요: {detail['consideration']}"
        detail_list.append(consideration)

    detail_format = "\n".join(detail_list)
    return detail_format
