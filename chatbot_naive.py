import os
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from tavily import TavilyClient

os.environ["TAVILY_API_KEY"] = "your_tavily_api"
os.environ["OPENAI_API_KEY"] = "your_openai_api"

# Tavily API를 사용하여 검색하는 함수
def tavily_search_tool(query):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    result = client.search(query, search_depth="advanced")["results"]
    return result

# 여행 일정을 생성하는 함수
def generate_schedule_response(agent, user_information, user_detail, user_message):
    prompt = f"""
    당신은 여행 계획 전문가입니다. 사용자가 여행 계획을 요청하면 Tavily 검색 도구를 활용하여 최고의 계획을 생성하십시오.

    ### 사용자 정보:
    1. 대화 중 사용자가 정보를 변경한다면, 변경한 정보를 반영합니다. 또한 변경한 정보를 메모리에도 반영합니다.
    2. **사용자 기본 정보**:
        {user_information}
    3. **사용자 디테일 정보**:
        {user_detail}

    ### 도구 사용 가이드:
    1. **Tavily 검색 도구**:
       - 실시간 정보나 최신 트렌드, 이벤트 정보를 검색합니다.
       - 계절에 따른 축제나 최근에 새로 생긴 관광지에 대한 정보를 제공합니다.
       - 검색 결과에는 장소, 이미지 URL이 포함될 수 있습니다.

    ### 형식:
    1. 여행 일정 계획을 요청한다면 무조건 이 형식을 따라야 합니다.
    2. 즉 다른 요청시에는 이 형식을 지킬 필요가 없습니다.
    3. 각 일정은 "n일차"로 나누어서 표시합니다.
    4. 각 일정에는 시간, 장소, 이동수단, 팁(선택 사항), 장소 사진(선택 사항)을 포함합니다.
    5. 일정은 구조적으로 표시하며, 예시는 다음과 같습니다:

    ###1일차
    **오전 08:00** 신주쿠 가든 구경
    (팁: 아침 일찍 가면 덜 붐빕니다)

    ↓ 버스 15번 이용
    ---------------------------------------------------------
    **오후 01:00** 아사쿠사 사찰 방문

    ↓ 도보로 이동
    ---------------------------------------------------------
    **오후 05:00** 스카이트리 전망대

    ### 형식:
    1. 사용자가 준비물 안내를 요청하면 답변합니다.
    2. 사용자가 요청을 하지 않으면 답변하지 않아도 됩니다.
    3. 예시는 다음과 같습니다:

    ###준비물
    1. **여권 및 여행 관련 서류**: 해외 여행을 위해서 필수입니다. 필요한 서류나 문서를 챙기세요.
    2. **편한 신발**: 도쿄 여행은 도보 이동이 많아 편안한 신발이 필수입니다.
    3. **가벼운 외투**: 1월의 도쿄는 추울 수 있으니 따뜻한 옷을 준비하세요.

    ### 사용자 요청:
    {user_message}

    **주의**: 위의 형식을 정확히 따르세요. 형식 오류가 있으면 재작성합니다.
    """
    response = agent.invoke(prompt)
    output = response['output']
    return output

def initialize_react_tools():
    """
    ReAct 도구 목록 초기화
    """
    tavily_search_tool_instance = Tool(
        name="search_tavily",
        func=tavily_search_tool,
        description=(
            "최신 트렌드, 실시간 정보, 이벤트 등을 검색합니다. "
            "유명 장소, 이벤트, 실시간 데이터를 제공합니다."
        ),
    )
    return [tavily_search_tool_instance]

# ReAct 에이전트 초기화
def initialize_react_agent(tools):
    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = ChatOpenAI(model="gpt-4o-mini", 
                     openai_api_key=os.getenv("OPENAI_API_KEY"),
                     # max_tokens=2000
                     )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="conversational-react-description",
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,  # 파싱 오류 핸들링 활성화
    )
    return agent

def chat_loop(agent, user_information, user_detail, user_message):
    response = generate_schedule_response(agent, user_information, user_detail, user_message)
    return response

def implementation(user_information, user_detail, user_message, agent=None):
    if agent is None:
        tools = initialize_react_tools()
        agent = initialize_react_agent(tools)

    bot_message = chat_loop(agent, user_information, user_detail, user_message)
    return bot_message

def tuning_run(user_information, user_detail, user_message):
    bot_message = implementation(user_information, user_detail, user_message)
    return bot_message
