import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "data" / "seed"
PASSWORD = "mock1234"


CATEGORIES = {
    "과학/기술": [
        ("AI", "AI 연구", "컴퓨터공학"),
        ("데이터 분석", "데이터 분석", "통계학"),
        ("로봇", "로봇 제작", "기계공학"),
        ("수학", "수학 튜터링", "수학"),
        ("양자역학", "양자정보 연구", "물리학"),
        ("코딩교육", "코딩 멘토링", "소프트웨어공학"),
        ("드론", "드론 제작", "항공공학"),
        ("메이커활동", "메이커 프로젝트", "융합공학"),
    ],
    "의료/바이오": [
        ("바이오", "바이오 데이터", "생명과학"),
        ("의료기술", "의료기술 기획", "의공학"),
        ("심리상담", "청소년 상담", "심리학"),
        ("응급처치", "응급처치 교육", "응급구조학"),
        ("운동처방", "운동처방", "스포츠의학"),
        ("영양관리", "영양 상담", "식품영양학"),
    ],
    "환경/에너지": [
        ("기후위기", "기후 데이터", "환경학"),
        ("환경보호", "환경 캠페인", "환경공학"),
        ("재생에너지", "재생에너지 프로젝트", "전기전자공학"),
        ("해양생물학", "해양 생태 탐사", "해양생물학"),
        ("도시농업", "도시농업 운영", "원예학"),
        ("등산", "생태 탐방", "체육학"),
    ],
    "예술/디자인": [
        ("디자인", "디자인 실습", "시각디자인"),
        ("사진", "사진 기록", "사진"),
        ("음악", "음악 제작", "음악학"),
        ("공연기획", "공연 기획", "공연예술"),
        ("웹툰", "웹툰 창작", "만화애니메이션"),
        ("패션스타일링", "패션 스타일링", "패션디자인"),
        ("공예", "공예 클래스", "공예디자인"),
    ],
    "미디어/콘텐츠": [
        ("영상제작", "영상 제작", "영상학"),
        ("글쓰기", "글쓰기 코칭", "문예창작"),
        ("저널리즘", "취재와 기사 작성", "언론정보학"),
        ("SF 독서", "SF 독서 모임", "국어국문학"),
        ("팟캐스트", "팟캐스트 운영", "방송콘텐츠"),
        ("숏폼콘텐츠", "숏폼 콘텐츠 제작", "미디어커뮤니케이션"),
        ("게임방송", "게임 방송", "게임콘텐츠"),
    ],
    "교육": [
        ("교육", "진로 교육", "교육학"),
        ("대중강연", "대중 강연", "교육공학"),
        ("독서모임", "독서 모임 운영", "문헌정보학"),
        ("토론", "토론 코칭", "사회교육"),
        ("멘토링", "청소년 멘토링", "상담교육"),
        ("학습코칭", "학습 코칭", "교육심리"),
    ],
    "사회/경영": [
        ("사회혁신", "사회혁신 프로젝트", "사회학"),
        ("창업", "창업 운영", "경영학"),
        ("브랜딩", "브랜딩 전략", "마케팅"),
        ("NGO활동", "NGO 캠페인", "정치외교학"),
        ("소셜모임운영", "소셜 모임 운영", "커뮤니티디자인"),
        ("아이돌팬클럽", "팬클럽 운영", "문화콘텐츠"),
        ("지역축제", "지역 축제 기획", "문화기획"),
        ("플리마켓", "플리마켓 운영", "유통경영"),
        ("반려동물커뮤니티", "반려동물 커뮤니티", "커뮤니티케어"),
    ],
    "농업/식품": [
        ("요리", "요리 클래스", "조리학"),
        ("식품개발", "식품 개발", "식품공학"),
        ("카페운영", "카페 운영", "외식경영"),
        ("정육유통", "정육 유통", "축산식품학"),
        ("로컬푸드", "로컬푸드 기획", "농업경제학"),
    ],
}


PROFILE_TEMPLATES = {
    "과학/기술": [
        ("연구원", "미래랩", "실험과 데이터를 연결해 학생들이 기술의 원리를 이해하도록 돕습니다."),
        ("엔지니어", "테크스튜디오", "작은 프로토타입을 만들며 문제 해결 과정을 안내합니다."),
        ("강사", "코드캠퍼스", "처음 배우는 학생도 따라올 수 있는 실습형 수업을 운영합니다."),
    ],
    "의료/바이오": [
        ("전문가", "헬스케어센터", "현장 사례를 바탕으로 건강과 바이오 분야 진로를 설명합니다."),
        ("코치", "웰니스랩", "몸과 마음을 돌보는 습관을 학생 눈높이에 맞춰 안내합니다."),
    ],
    "환경/에너지": [
        ("활동가", "그린액션", "지역의 환경 문제를 찾고 직접 해결하는 프로젝트를 운영합니다."),
        ("컨설턴트", "에코파트너스", "기후와 에너지 전환을 생활 속 사례로 풀어냅니다."),
    ],
    "예술/디자인": [
        ("디렉터", "크리에이티브룸", "취향과 메시지를 시각 결과물로 만드는 과정을 코칭합니다."),
        ("작가", "프리랜서", "포트폴리오와 창작 루틴을 함께 점검합니다."),
    ],
    "미디어/콘텐츠": [
        ("PD", "콘텐츠스튜디오", "기획, 촬영, 편집, 발행까지 콘텐츠 제작 흐름을 안내합니다."),
        ("에디터", "미디어랩", "좋은 질문을 글과 영상으로 바꾸는 방법을 알려줍니다."),
    ],
    "교육": [
        ("교사", "미래학교", "학생 맞춤 프로젝트 수업과 진로 상담을 운영합니다."),
        ("퍼실리테이터", "러닝커뮤니티", "모임과 수업에서 사람들이 배우도록 돕는 역할을 합니다."),
    ],
    "사회/경영": [
        ("운영자", "커뮤니티하우스", "사람을 모으고 규칙을 만들며 지속 가능한 활동을 설계합니다."),
        ("기획자", "임팩트랩", "작은 아이디어를 실제 프로젝트와 수익 모델로 연결합니다."),
    ],
    "농업/식품": [
        ("대표", "로컬푸드랩", "먹거리와 지역 자원을 연결하는 현장 경험을 나눕니다."),
        ("개발자", "푸드스튜디오", "레시피와 상품 개발 과정을 학생 눈높이로 설명합니다."),
    ],
}


SURNAMES = "김이박최정강조윤장임한오서신권황안송류홍전문양손배백허남심노하곽성차주우"
GIVEN = [
    "서준", "민지", "지우", "하린", "도윤", "서연", "유진", "현우", "민재", "서아",
    "지호", "나윤", "연우", "시윤", "다은", "예준", "수아", "준서", "채원", "하준",
]
SCHOOLS = ["미래중학교", "한빛고등학교", "늘봄고등학교", "하늘중학교", "새롬고등학교", "은하중학교", "서울미래대학교", "지역학습센터"]


def write_csv(name, rows, fields):
    path = SEED_DIR / name
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def person_name(i):
    return SURNAMES[i % len(SURNAMES)] + GIVEN[(i * 7) % len(GIVEN)]


def nickname(node, i):
    suffixes = ["길잡이", "메이커", "코치", "운영자", "기획자", "탐험가", "쌤", "디렉터", "메이트", "연구가"]
    clean = node.replace("/", "").replace(" ", "")
    return f"{clean}{suffixes[i % len(suffixes)]}"[:10]


def build_experts():
    experts = []
    nodes = []
    flat = [(field, node, role, major) for field, entries in CATEGORIES.items() for node, role, major in entries]
    for i in range(150):
        field, primary_node, role, major = flat[i % len(flat)]
        title, org_suffix, description = PROFILE_TEMPLATES[field][(i // len(flat)) % len(PROFILE_TEMPLATES[field])]
        login_id = f"id_e_{i + 1:03d}"
        org = f"{primary_node}{org_suffix}" if org_suffix != "프리랜서" else "프리랜서"
        current_job = f"{role} {title}"
        experts.append({
            "login_id": login_id,
            "nickname": nickname(primary_node, i),
            "title": current_job,
            "organization": org,
            "major": major,
            "current_job": current_job,
            "field": field,
            "description": description,
            "contact_email": f"{login_id}@future.example",
            "is_approved": "1",
        })
        field_nodes = [entry[0] for entry in CATEGORIES[field]]
        cross_field = flat[(i * 5 + 11) % len(flat)][1]
        selected = [primary_node, field_nodes[(i + 2) % len(field_nodes)], cross_field]
        for node in dict.fromkeys(selected):
            nodes.append({"login_id": login_id, "node_name": node})
    return experts, nodes


def build_students(all_nodes):
    students = []
    universes = []
    levels = [("중학생", "2학년"), ("중학생", "3학년"), ("고등학생", "1학년"), ("고등학생", "2학년"), ("대학생", "해당없음"), ("성인", "해당없음")]
    for i in range(300):
        login_id = f"id_s_{i + 1:03d}"
        level, grade = levels[i % len(levels)]
        school = SCHOOLS[i % len(SCHOOLS)]
        if level == "대학생":
            school = "서울미래대학교"
        elif level == "성인":
            school = "지역학습센터"
        students.append({
            "login_id": login_id,
            "nickname": person_name(i),
            "school_level": level,
            "school_name": school,
            "grade": grade,
        })
        for offset in range(3 + (i % 3)):
            universes.append({
                "login_id": login_id,
                "node_name": all_nodes[(i * 3 + offset * 7) % len(all_nodes)],
            })
    return students, universes


QUESTION_PATTERNS = [
    (
        "{node} 활동을 처음 시작할 때 혼자 해볼 만한 일이 있을까요?",
        "요즘 이 분야에 관심이 생겼는데, 주변에 같이 하는 친구가 많지 않습니다. 혼자 시작해도 의미 있는 활동과 한 달 안에 남길 수 있는 기록 방식이 궁금합니다.",
    ),
    (
        "{node} 포트폴리오를 만들 때 보여줘야 하는 핵심이 뭘까요?",
        "좋아한다는 말만으로는 부족할 것 같아서 작은 포트폴리오를 만들고 싶습니다. 완성작, 과정 기록, 피드백 중 무엇을 더 중요하게 봐야 할까요?",
    ),
    (
        "학교 수업에서 배운 내용을 {node} 활동으로 연결하고 싶습니다.",
        "수업 시간에 배운 내용이 재미있었는데, 이 활동과 연결하면 더 깊게 탐구할 수 있을 것 같습니다. 선생님께 제안할 만한 작은 프로젝트 형태가 있을까요?",
    ),
    (
        "{node} 분야에 관심은 있지만 실력이 부족해서 시작이 망설여집니다.",
        "관심은 큰데 막상 해보면 결과물이 어설퍼서 금방 포기하게 됩니다. 초보자가 실력을 확인하면서도 지치지 않게 연습하는 방법을 알고 싶습니다.",
    ),
    (
        "{node} 모임을 친구들과 운영한다면 어떤 규칙이 필요할까요?",
        "친구 몇 명과 {node} 관련 활동을 해보려고 합니다. 처음에는 재미있게 시작해도 역할 분담이나 일정 때문에 흐지부지될까 봐 걱정됩니다.",
    ),
    (
        "{node} 분야가 진로로 이어질 수 있는지 현실적으로 확인하고 싶습니다.",
        "{node}에 관심이 있지만 이걸 직업이나 활동 방향으로 삼아도 되는지 잘 모르겠습니다. 좋아하는 마음과 실제 진로 가능성을 어떻게 구분하면 좋을까요?",
    ),
    (
        "{node} 활동을 생활기록부나 자기소개서에 쓰려면 어떤 깊이가 필요할까요?",
        "단순 체험으로 끝내지 않고 제 관심과 성장 과정이 보이게 만들고 싶습니다. 어떤 질문을 잡고 어떤 증거를 남겨야 의미 있는 활동이 될까요?",
    ),
    (
        "{node} 분야를 잘하는 사람들은 초반에 무엇을 다르게 하나요?",
        "자료를 찾아보면 다들 결과가 좋아 보여서 더 어렵게 느껴집니다. 초반에 시행착오를 줄이는 습관이나 관찰 포인트가 있다면 알고 싶습니다.",
    ),
    (
        "{node} 활동에서 팀장 역할을 맡게 됐는데 부담됩니다.",
        "제가 제안해서 시작한 활동이라 팀장을 맡게 됐습니다. 친구들이 편하게 참여하면서도 결과물을 남기려면 어떤 방식으로 운영해야 할까요?",
    ),
    (
        "{node} 분야와 관련된 책, 영상, 현장 경험 중 무엇부터 해야 할까요?",
        "관심 분야를 넓히고 싶은데 책을 읽어야 할지, 영상을 봐야 할지, 직접 체험을 해야 할지 모르겠습니다. 순서를 정하는 기준이 궁금합니다.",
    ),
    (
        "{node} 활동을 취미가 아니라 프로젝트처럼 발전시키고 싶습니다.",
        "지금은 재미로만 하고 있는데, 조금 더 제대로 된 활동으로 만들어 보고 싶습니다. 주제 선정부터 결과 공유까지 어떤 흐름으로 잡으면 좋을까요?",
    ),
    (
        "{node} 분야에서 흔히 하는 오해나 실수가 있을까요?",
        "처음 시작하는 입장에서 겉으로 보이는 모습만 보고 판단할까 봐 걱정됩니다. 실제 현장이나 활동 경험에서 느낀 오해를 알려주시면 도움이 될 것 같습니다.",
    ),
]

STUDENT_CONTEXTS = [
    "중학교 동아리에서 작은 발표를 준비하는 상황",
    "고등학교 수행평가와 개인 관심사를 연결하려는 상황",
    "친구 두 명과 방과 후 프로젝트를 시작하려는 상황",
    "아직 결과물은 없지만 관련 자료를 모으기 시작한 상황",
    "진로를 확정하기보다는 탐색 증거를 만들고 싶은 상황",
    "학교 밖 커뮤니티나 온라인 모임 참여를 고민하는 상황",
]


def build_question(i, node):
    title_tpl, body_tpl = QUESTION_PATTERNS[i % len(QUESTION_PATTERNS)]
    context = STUDENT_CONTEXTS[(i * 5) % len(STUDENT_CONTEXTS)]
    title = title_tpl.format(node=node)
    body = body_tpl.format(node=node)
    endings = [
        "제가 바로 해볼 수 있는 첫 단계를 구체적으로 알려주세요.",
        "실패했을 때 어떻게 기록하면 좋을지도 궁금합니다.",
        "학생 수준에서 무리하지 않는 범위로 조언 부탁드립니다.",
        "나중에 다시 질문드릴 때 어떤 결과를 가져오면 좋을까요?",
    ]
    text = f"{context}입니다. {body} {endings[i % len(endings)]}"
    return title, text

FIELD_ADVICE = {
    "과학/기술": {
        "first": "작게라도 직접 만들어 보는 경험이 가장 빠릅니다. 검색해서 이해한 내용과 내가 손으로 구현한 내용은 기억에 남는 깊이가 완전히 다릅니다.",
        "project": "추천하는 첫 결과물은 '문제 정의 한 장 + 실험 기록 + 실패 원인'입니다. 코드나 장치가 완벽하지 않아도 실험을 설계하고 고친 흔적이 있으면 충분히 강한 포트폴리오가 됩니다.",
        "check": "수학이나 코딩 실력만 보지 말고, 데이터를 어떻게 모았는지와 결과를 어떻게 설명했는지를 함께 점검하세요.",
    },
    "의료/바이오": {
        "first": "이 분야는 사람을 이해하는 태도와 정확한 기록 습관이 중요합니다. 멋진 지식보다 관찰을 차분히 남기는 연습이 먼저입니다.",
        "project": "건강 뉴스 하나를 골라 근거, 대상, 한계, 내 생각을 구분해 정리해 보세요. 의료와 바이오는 '확신'보다 '근거를 다루는 법'을 보여주는 기록이 좋습니다.",
        "check": "실제 현장은 협업이 많으니 생명과학, 통계, 윤리, 커뮤니케이션 중 내가 어느 쪽에 강한지도 같이 살펴보면 좋습니다.",
    },
    "환경/에너지": {
        "first": "환경 활동은 멀리 있는 거대한 문제처럼 보이지만, 출발은 우리 동네 관찰입니다. 학교 주변 쓰레기, 전기 사용, 식물 분포처럼 매주 볼 수 있는 대상을 정하세요.",
        "project": "사진 기록, 간단한 수치 측정, 해결 제안까지 묶으면 좋은 프로젝트가 됩니다. 변화 전후를 비교할 수 있으면 더 좋고요.",
        "check": "좋은 의도만으로 끝나지 않게 이해관계자와 비용, 지속 가능성을 함께 적어 보세요.",
    },
    "예술/디자인": {
        "first": "취향을 부끄러워하지 말고 많이 모으세요. 다만 '예뻐서'에서 멈추지 말고 왜 끌리는지 색, 리듬, 재료, 이야기로 나눠 적어야 실력이 됩니다.",
        "project": "첫 포트폴리오는 완성작 세 개보다 과정이 보이는 한 프로젝트가 낫습니다. 참고 자료, 시안, 버린 선택, 최종안의 이유를 함께 보여주세요.",
        "check": "다른 사람에게 보여주고 '무엇이 먼저 보였는지'를 물어보세요. 창작자는 의도와 전달 사이의 차이를 줄이는 훈련이 중요합니다.",
    },
    "미디어/콘텐츠": {
        "first": "콘텐츠는 아이디어보다 발행 리듬이 더 중요할 때가 많습니다. 처음부터 대작을 만들기보다 같은 주제로 짧은 결과물을 세 번 내보세요.",
        "project": "기획 의도, 대상 독자, 제목 후보, 썸네일 또는 첫 문장, 반응 기록을 남기면 실제 제작자처럼 보입니다.",
        "check": "조회수만 보지 말고 사람들이 어디에서 멈췄는지, 어떤 문장에 반응했는지, 다음 편을 보고 싶어 하는지 확인하세요.",
    },
    "교육": {
        "first": "누군가에게 설명해 보는 순간 내 이해도가 드러납니다. 친구 한 명에게 10분짜리 미니 수업을 해보고 질문을 받아 보세요.",
        "project": "좋은 교육 프로젝트는 자료가 화려한 것보다 학습자가 전보다 무엇을 할 수 있게 되었는지가 보여야 합니다.",
        "check": "설명, 활동, 피드백, 다시 해보기의 흐름이 있는지 확인하세요. 이 네 가지가 있으면 작은 활동도 교육 경험으로 기록할 수 있습니다.",
    },
    "사회/경영": {
        "first": "사람이 모이는 활동은 기획보다 운영에서 진짜 실력이 보입니다. 모임 규칙, 역할 분담, 갈등 처리, 지속 가능한 일정이 핵심입니다.",
        "project": "팬클럽, 소셜모임, 플리마켓 같은 활동도 충분히 포트폴리오가 됩니다. 참여자 수보다 '왜 사람들이 계속 왔는지'를 설명할 수 있어야 합니다.",
        "check": "예산, 홍보 채널, 운영 시간, 만족도, 다음 운영을 위한 개선점을 숫자와 사례로 남기세요.",
    },
    "농업/식품": {
        "first": "먹거리 분야는 손으로 해보는 경험이 강합니다. 레시피, 원가, 위생, 고객 반응을 함께 기록하면 단순 취미를 넘어서 보입니다.",
        "project": "작은 시식회나 메뉴 테스트를 열고 반응을 표로 정리해 보세요. 맛의 감상뿐 아니라 가격, 포장, 보관, 재구매 의사를 물어보면 좋습니다.",
        "check": "좋아하는 음식과 팔 수 있는 음식은 다를 수 있습니다. 만드는 사람의 즐거움과 이용자의 편의 사이를 비교해 보세요.",
    },
}

ANSWER_STYLES = [
    {
        "open": "좋은 질문이에요. {node} 분야는 처음부터 크게 잡으면 금방 막히기 쉬워서, 작게 해보고 기록하는 방식이 잘 맞습니다.",
        "close": "결과가 작아 보여도 괜찮습니다. 대신 날짜, 선택한 이유, 배운 점을 남기세요. 그 기록이 다음 질문의 수준을 올려줍니다.",
    },
    {
        "open": "조금 직설적으로 말해볼게요. {node} 분야는 관심만으로는 잘 보이지 않고, 남이 확인할 수 있는 흔적이 있어야 설득력이 생깁니다.",
        "close": "한 달 뒤에 '이걸 보고 다른 사람이 나를 다시 찾을 이유가 있나?'라고 물어보세요. 답이 애매하면 범위를 줄여 다시 만들면 됩니다.",
    },
    {
        "open": "지금 단계에서 가장 중요한 건 잘하는 척하기보다 오래 붙잡을 수 있는 방식을 찾는 거예요. {node}도 처음에는 가볍게 시작해도 충분합니다.",
        "close": "불안하면 목표를 더 작게 잡으세요. 작은 성공이 쌓이면 자신감이 생기고, 그때부터는 더 어려운 활동도 자연스럽게 시도하게 됩니다.",
    },
    {
        "open": "{node}를 프로젝트로 만든다고 생각해 봅시다. 핵심은 주제, 대상, 결과물, 피드백 루프를 분명히 하는 것입니다.",
        "close": "완료 후에는 결과물만 올리지 말고 운영 로그를 같이 정리하세요. 무엇을 바꿨는지 보이는 사람이 다음 기회를 더 잘 잡습니다.",
    },
    {
        "tone": "선배 같은 조언자",
        "open": "저라면 {node} 분야를 바로 진로 이름으로 고정하지는 않을 것 같아요. 대신 이 활동을 하면서 내가 어떤 순간에 몰입하는지부터 볼 겁니다.",
        "close": "진로는 한 번에 정답을 찍는 일이 아니라 증거를 모으는 일에 가깝습니다. 이번 달에는 그 증거 하나를 만드는 데 집중해 보세요.",
    },
]


def _question_focus(question_title):
    if "포트폴리오" in question_title or "생활기록부" in question_title or "자기소개서" in question_title:
        return "portfolio"
    if "팀" in question_title or "모임" in question_title or "팀장" in question_title:
        return "team"
    if "진로" in question_title or "현실" in question_title:
        return "career"
    if "학교" in question_title or "수업" in question_title:
        return "school"
    if "실력" in question_title or "초반" in question_title:
        return "practice"
    return "start"


def build_answer_text(field, node, question_title, question_text, expert, index):
    advice = FIELD_ADVICE.get(field, FIELD_ADVICE["사회/경영"])
    style = ANSWER_STYLES[(index + len(node) + len(question_title) + len(expert["login_id"])) % len(ANSWER_STYLES)]
    current_job = expert["current_job"]
    organization = expert["organization"]
    title = question_title.rstrip("?")
    focus = _question_focus(question_title)
    seed = index % 10

    intro = (
        f"{style['open'].format(node=node)} 저는 {organization}에서 {current_job} 역할로 활동하면서 "
        f"'{title}' 같은 질문을 여러 번 받아봤습니다."
    )

    if focus == "portfolio":
        bodies = [
            (
                f"{intro}\n\n"
                f"포트폴리오에서 가장 먼저 보는 건 완성도보다 '판단의 흔적'입니다. {advice['project']} "
                f"처음 세운 질문, 참고한 자료, 내가 버린 선택지, 피드백 후 고친 부분을 같이 보여주세요.\n\n"
                f"구성은 네 칸이면 충분합니다. 1) 왜 이 주제를 골랐는지 2) 어떤 기준으로 해봤는지 3) 무엇이 잘 안 됐는지 4) 다음엔 무엇을 바꿀지입니다. "
                f"특히 {node}에서는 결과물이 작아도 과정을 설명할 수 있으면 훨씬 진짜처럼 보입니다.\n\n"
                f"가능하면 친구나 선생님 한 명에게 보여주고 질문을 받아보세요. 그 질문에 답하면서 보완한 내용까지 넣으면, 단순 체험이 아니라 성장 기록이 됩니다. {style['close']}"
            ),
            (
                f"포트폴리오를 만들겠다는 방향은 좋아요. 다만 처음부터 멋진 산출물을 목표로 잡으면 오래 못 갑니다.\n\n"
                f"제가 추천하는 방식은 '작은 결과물 2개 + 비교 글 1개'입니다. 예를 들어 {node}와 관련해 서로 다른 방법을 두 번 시도하고, 어떤 방식이 왜 더 나았는지 적어보세요. "
                f"{advice['check']} 이 비교가 있어야 보는 사람이 학생의 생각을 읽을 수 있습니다.\n\n"
                f"마지막 페이지에는 자랑보다 다음 질문을 적으세요. '아직 모르겠는 점', '다음에 검증할 점', '도움을 받고 싶은 점'이 있는 포트폴리오가 오히려 더 성숙해 보입니다."
            ),
        ]
        return bodies[seed % len(bodies)]

    if focus == "team":
        bodies = [
            (
                f"{intro}\n\n"
                f"팀 활동에서 제일 중요한 건 의욕보다 운영 규칙입니다. {advice['first']} "
                f"처음 모일 때 역할을 '잘하는 사람' 기준으로 나누지 말고, 기록 담당, 일정 담당, 결과물 담당, 피드백 담당처럼 행동 기준으로 나누세요.\n\n"
                f"회의는 길게 하지 않는 편이 좋습니다. 매번 '지난번에 한 일, 이번에 할 일, 막힌 점' 세 가지만 확인하세요. "
                f"{node} 활동이 재미로 시작했더라도 이 세 가지가 남으면 프로젝트가 됩니다.\n\n"
                f"갈등이 생기면 사람을 평가하지 말고 약속을 다시 보세요. 누가 못했는지가 아니라 약속이 너무 컸는지, 일정이 애매했는지, 역할이 겹쳤는지를 점검하면 분위기가 덜 상합니다."
            ),
            (
                f"팀장 역할이 부담된다는 말이 오히려 좋은 신호예요. 부담을 느끼는 사람은 대체로 팀을 방치하지 않거든요.\n\n"
                f"저라면 {node} 모임을 시작할 때 첫 모임에서 세 문장을 정하게 하겠습니다. '우리는 무엇을 만들 것인가', '언제까지 할 것인가', '안 해도 되는 것은 무엇인가'. "
                f"세 번째 문장이 특히 중요합니다. 욕심을 줄여야 끝까지 갑니다.\n\n"
                f"결과물은 한 번에 크게 만들지 말고 매주 작은 공개를 하세요. 사진 한 장, 진행표 한 장, 짧은 후기 하나면 됩니다. "
                f"나중에 돌아보면 그 조각들이 활동 기록이 되고, 팀원들도 자기가 참여했다는 감각을 얻습니다."
            ),
        ]
        return bodies[seed % len(bodies)]

    if focus == "career":
        bodies = [
            (
                f"진로로 볼 수 있는지 확인하려면, '좋아함'과 '버틸 수 있음'을 나눠 봐야 합니다.\n\n"
                f"{node}에서 재미있는 장면만 보면 누구나 끌립니다. 그런데 실제 활동에는 반복 작업, 피드백, 일정 조율, 기록 같은 덜 멋진 일이 따라옵니다. "
                f"저는 학생들에게 일부러 그 덜 멋진 일을 2주 동안 해보라고 말합니다. 거기서도 계속 궁금하면 꽤 좋은 신호입니다.\n\n"
                f"{advice['check']} 그리고 관련 직업 이름을 하나로 고정하지 마세요. 같은 {node}라도 연구, 운영, 교육, 콘텐츠, 창업처럼 여러 방향이 있습니다. "
                f"이번 달에는 직업을 정하기보다 내가 어떤 역할에 가까운지 증거를 모아보세요."
            ),
            (
                f"{intro}\n\n"
                f"현실성은 인터넷 검색보다 작은 실험에서 더 잘 보입니다. {advice['first']} "
                f"해보고 나서 '시간이 빨리 갔는지', '막혀도 다시 찾게 되는지', '다른 사람에게 설명하고 싶은지'를 체크하세요.\n\n"
                f"반대로 결과가 좋았는데도 과정이 너무 싫었다면 진로로는 다시 생각해볼 필요가 있습니다. 좋아하는 분야와 잘 맞는 일의 형태는 다를 수 있어요. "
                f"{node} 자체가 좋은지, {node}를 둘러싼 사람/도구/표현 방식 중 무엇이 좋은지 분리해서 보면 선택지가 넓어집니다."
            ),
        ]
        return bodies[seed % len(bodies)]

    if focus == "school":
        return (
            f"학교 수업과 연결하려는 접근은 아주 좋습니다. 선생님 입장에서도 그냥 '하고 싶어요'보다 수업 개념과 연결된 제안이 훨씬 도와주기 쉽습니다.\n\n"
            f"제안서는 길 필요 없습니다. 한 장에 적어보세요. 수업에서 배운 개념을 이 활동으로 연결하는 방법, 결과물 형태, 필요한 도움을 네 줄로 정리하면 됩니다. "
            f"{advice['project']} 이때 결과물은 발표 자료 하나보다 활동 전후가 비교되는 기록이 좋습니다.\n\n"
            f"예를 들어 수업 개념을 설명하는 카드뉴스, 짧은 실험 영상, 친구 설문 결과, 모임 운영 기록처럼 교실 밖으로 조금 나간 형태가 좋습니다. "
            f"마지막에는 '수업에서 배운 것을 해보니 달라진 생각'을 꼭 적으세요. 그 문장이 활동을 단순 과제에서 탐구로 바꿔줍니다."
        )

    if focus == "practice":
        return (
            f"실력이 부족해서 망설여진다면, 지금은 평가받을 결과물보다 반복 가능한 연습 구조가 먼저입니다.\n\n"
            f"저라면 {node}를 3단계로 나눠 보겠습니다. 첫 주는 따라 하기, 둘째 주는 아주 작은 변형, 셋째 주는 누군가에게 보여주고 피드백 받기입니다. "
            f"{advice['first']} 잘하려고 시작하면 부담이 커지고, 관찰하려고 시작하면 계속할 수 있습니다.\n\n"
            f"연습 기록에는 점수를 매기지 마세요. 대신 '오늘 알게 된 것', '아직 헷갈리는 것', '다음에 바꿀 것'만 적으세요. "
            f"이 세 가지가 쌓이면 실력이 느는 방향이 보입니다. 그리고 어느 순간부터는 결과물보다 내가 고치는 속도가 빨라졌다는 걸 느끼게 될 거예요."
        )

    if "오해" in question_title or "실수" in question_title:
        return (
            f"{node}에서 흔한 오해는 '잘하는 사람은 처음부터 감이 좋다'는 생각입니다. 실제로는 감보다 기록과 수정이 더 많이 작동합니다.\n\n"
            f"제가 본 좋은 초보자는 질문을 빨리 바꿉니다. 처음에는 '어떻게 잘하나요'라고 묻지만, 조금 지나면 '왜 이 부분에서 막히나요', '누구에게 보여줘야 하나요', '무엇을 줄여야 하나요'라고 묻습니다. "
            f"{advice['check']}\n\n"
            f"또 하나의 실수는 너무 빨리 진로 결론을 내리는 것입니다. {node}가 맞는지 아닌지는 한 번의 체험으로 판단하기 어렵습니다. "
            f"작게 세 번 해보고, 매번 다른 방식으로 기록해 보세요. 그 뒤에도 계속 질문이 생긴다면 그건 꽤 좋은 신호입니다."
        )

    openings = [
        f"{intro}\n\n제가 추천하는 첫 단계는 아주 작습니다.",
        f"바로 큰 계획을 세우기보다, {node}를 '2주 실험'으로 다뤄보면 좋겠습니다.",
        f"이 질문은 정답 하나보다 순서가 중요합니다. 저는 다음 순서로 해보라고 말하고 싶어요.",
    ]
    return (
        f"{openings[seed % len(openings)]} {advice['first']} "
        f"자료를 찾는 데서 끝내지 말고 직접 해본 흔적을 남기세요. 사진, 짧은 메모, 실패한 시도도 괜찮습니다.\n\n"
        f"그다음은 다른 사람에게 보여주는 단계입니다. {advice['project']} "
        f"보여줄 사람이 꼭 전문가일 필요는 없습니다. 친구 한 명에게 설명해보고, 무엇이 이해됐고 무엇이 흐렸는지 물어보세요.\n\n"
        f"마지막으로 다음 질문을 만들어 오세요. {advice['check']} "
        f"'{node} 분야에 관심이 있어요'보다 '이걸 해봤더니 이 부분이 막혔어요'가 훨씬 강한 질문입니다. {style['close']}"
    )


ANSWER_ADDONS = [
    "덧붙이면, 활동을 마친 뒤에는 반드시 '다음에 물어볼 질문'을 하나 남겨두세요. 좋은 탐색은 답을 하나 얻고 끝나는 것이 아니라, 더 정확한 질문으로 이동하는 과정입니다. 다음 질문이 구체적일수록 전문가에게 받을 수 있는 조언도 훨씬 실질적으로 바뀝니다.",
    "기록 방식도 중요합니다. 날짜별로 무엇을 했는지 적는 것에서 멈추지 말고, 왜 그렇게 판단했는지와 다른 선택지는 무엇이었는지를 함께 남겨보세요. 나중에 보면 그 부분이 가장 강한 성장 증거가 됩니다.",
    "부모님이나 선생님께 보여줄 때는 결과만 말하지 말고, 내가 어떤 도움을 받으면 다음 단계로 갈 수 있는지도 같이 말해보세요. '더 해보고 싶다'보다 '이 부분을 검증해보고 싶다'가 훨씬 설득력 있습니다.",
    "시간 계획은 짧게 잡는 편이 좋습니다. 한 달 계획보다 10일 계획이 실제로 움직이기 쉽고, 10일 뒤에 계속할지 방향을 바꿀지 판단할 수 있습니다. 진로 탐색은 오래 고민하는 것보다 작게 실행하고 자주 고치는 쪽이 더 안전합니다.",
    "혹시 결과가 마음에 들지 않아도 그건 실패가 아닙니다. 무엇이 어려웠는지, 어떤 조건이 부족했는지, 누구에게 물어봐야 하는지를 알게 되었다면 이미 다음 단계의 자료를 얻은 것입니다.",
    "마지막으로, 이 활동을 혼자만의 관심으로 두지 말고 한 번은 다른 사람에게 설명해보세요. 설명하다가 막히는 부분이 바로 더 배워야 할 부분이고, 상대가 흥미를 보이는 부분이 다음 결과물의 방향이 될 수 있습니다.",
]


def polish_answer_text(text, node, index):
    replacements = {
        f"{node}를 ": f"{node} 활동을 ",
        f"{node}가 ": f"{node} 분야가 ",
        f"{node}와 ": f"{node} 분야와 ",
        f"{node}로 ": f"{node} 활동으로 ",
        f"{node}는 ": f"{node} 분야는 ",
        f"{node} 분야가 좋아요": f"{node} 분야에 관심이 있어요",
        f"{node} 활동으로 바꿔 해볼 활동": "이 활동으로 연결해 볼 내용",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)

    addon_idx = index % len(ANSWER_ADDONS)
    while len(text) < 850:
        text = f"{text}\n\n{ANSWER_ADDONS[addon_idx % len(ANSWER_ADDONS)]}"
        addon_idx += 2
    return text


def build_questions(experts, expert_nodes):
    nodes_by_expert = defaultdict(list)
    for row in expert_nodes:
        nodes_by_expert[row["login_id"]].append(row["node_name"])
    questions = []
    answers = []
    base = datetime(2026, 3, 1, 9, 20)
    for i in range(200):
        expert = experts[(i * 7) % len(experts)]
        student_login = f"id_s_{(i * 11) % 300 + 1:03d}"
        node = nodes_by_expert[expert["login_id"]][i % len(nodes_by_expert[expert["login_id"]])]
        title, text = build_question(i, node)
        asked_at = base + timedelta(hours=i * 9)
        qid = f"q_{i + 1:03d}"
        questions.append({
            "seed_id": qid,
            "from_login_id": student_login,
            "to_expert_login_id": expert["login_id"],
            "question_title": title,
            "question_text": text,
            "is_public": "1" if i % 9 else "0",
            "created_at": asked_at.isoformat(timespec="seconds"),
        })
        if i % 5 != 0:
            answer_text = build_answer_text(expert["field"], node, title, text, expert, i)
            answers.append({
                "seed_question_id": qid,
                "answer_text": polish_answer_text(answer_text, node, i),
                "answered_by_login_id": expert["login_id"],
                "is_new_for_asker": "1" if i % 4 == 0 else "0",
                "created_at": (asked_at + timedelta(days=1 + (i % 6), hours=2)).isoformat(timespec="seconds"),
            })
    return questions, answers


def main():
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    experts, expert_nodes = build_experts()
    all_nodes = sorted({row["node_name"] for row in expert_nodes})
    students, student_universes = build_students(all_nodes)
    questions, answers = build_questions(experts, expert_nodes)

    accounts = []
    accounts.extend({"login_id": row["login_id"], "password": PASSWORD, "role": "expert", "tokens": "5000"} for row in experts)
    accounts.extend({"login_id": row["login_id"], "password": PASSWORD, "role": "student", "tokens": "10000"} for row in students)

    write_csv("accounts.csv", accounts, ["login_id", "password", "role", "tokens"])
    write_csv("expert_profiles.csv", experts, ["login_id", "nickname", "title", "organization", "major", "current_job", "field", "description", "contact_email", "is_approved"])
    write_csv("expert_nodes.csv", expert_nodes, ["login_id", "node_name"])
    write_csv("student_profiles.csv", students, ["login_id", "nickname", "school_level", "school_name", "grade"])
    write_csv("student_univers.csv", student_universes, ["login_id", "node_name"])
    write_csv("questions.csv", questions, ["seed_id", "from_login_id", "to_expert_login_id", "question_title", "question_text", "is_public", "created_at"])
    write_csv("question_answers.csv", answers, ["seed_question_id", "answer_text", "answered_by_login_id", "is_new_for_asker", "created_at"])
    print(f"Generated {len(experts)} experts, {len(students)} students, {len(questions)} questions, {len(answers)} answers.")


if __name__ == "__main__":
    main()
