import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import io
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI

load_dotenv(override=True)
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_STORAGE_NAME = os.getenv("AZURE_STORAGE_NAME")
AZURE_STORAGE_CONNECTION_KEY = os.getenv("AZURE_STORAGE_CONNECTION_KEY")

OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SEARCHSERVICE_KEY = os.getenv("SEARCHSERVICE_KEY")
SEARCHSERVICE_ENDPOINT = os.getenv("SEARCHSERVICE_ENDPOINT")

def init_session_state():
    """세션 상태 초기화"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'page1'
    
    if 'project_config' not in st.session_state:
        st.session_state.project_config = {
            'project_name': '',
            'group_id': '',
            'artifact_id': '',
            'package_name': '',
            'description': '',
            'java_version': '17',
            'spring_boot_version': '3.2.0',
            'architecture_type': 'monolithic',
            'architecture_pattern': 'mvc',
            'database': 'mysql',
            # 'csv_file': None,
            'additional_requirements': ''
        }

def render_project_metadata_section():
    """프로젝트 메타데이터 섹션"""
    st.subheader("📋 Project Metadata")
    
    col1, col2 = st.columns(2)
    
    with col1:
        group_id = st.text_input(
            "Group",
            value=st.session_state.project_config['group_id'],
            placeholder="com.example"
        )
        
        artifact_id = st.text_input(
            "Artifact",
            value=st.session_state.project_config['artifact_id'],
            placeholder="demo"
        )
        
        project_name = st.text_input(
            "Name",
            value=st.session_state.project_config['project_name'],
            placeholder="demo"
        )
    
    with col2:
        description = st.text_input(
            "Description",
            value=st.session_state.project_config['description'],
            placeholder="Demo project for Spring Boot"
        )
        
        package_name = st.text_input(
            "Package name",
            value=st.session_state.project_config['package_name'],
            placeholder="com.example.demo"
        )
    
    # 세션 상태 업데이트
    st.session_state.project_config.update({
        'group_id': group_id,
        'artifact_id': artifact_id,
        'project_name': project_name,
        'description': description,
        'package_name': package_name
    })

def render_project_settings_section():
    """프로젝트 설정 섹션"""
    st.subheader("⚙️ Project Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        java_version = st.selectbox(
            "Java Version",
            options=['8', '11', '17', '21'],
            index=2  # 기본값: 17
        )
    
    with col2:
        spring_boot_version = st.selectbox(
            "Spring Boot Version",
            options=['3.2.0', '3.1.5', '3.0.12', '2.7.17'],
            index=0  # 기본값: 3.2.0
        )
    
    with col3:
        packaging = st.selectbox(
            "Packaging",
            options=['Jar', 'War'],
            index=0
        )
    
    # 세션 상태 업데이트
    st.session_state.project_config.update({
        'java_version': java_version,
        'spring_boot_version': spring_boot_version,
        'packaging': packaging.lower()
    })

def render_architecture_section():
    """아키텍처 선택 섹션"""
    st.subheader("🏗️ Architecture Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Architecture Type**")
        architecture_type = st.radio(
            "Choose architecture type:",
            options=['monolithic', 'msa'],
            format_func=lambda x: {
                'monolithic': '🏢 Monolithic',
                'msa': '🔗 Microservices (MSA)'
            }[x],
            key="arch_type"
        )
        
        if architecture_type == 'monolithic':
            st.info("💡 Single deployable unit with all features in one application")
        else:
            st.info("💡 Distributed system with multiple independent services")
    
    with col2:
        st.write("**Architecture Pattern**")
        architecture_pattern = st.radio(
            "Choose architecture pattern:",
            options=['mvc', 'hexagonal'],
            format_func=lambda x: {
                'mvc': '🎯 MVC (Model-View-Controller)',
                'hexagonal': '⬡ Hexagonal (Ports & Adapters)'
            }[x],
            key="arch_pattern"
        )
        
        if architecture_pattern == 'mvc':
            st.info("💡 Traditional layered architecture with Controllers, Services, Repositories")
        else:
            st.info("💡 Clean architecture with domain at center, isolated from external concerns")
    
    # 세션 상태 업데이트를 여기로 이동
    st.session_state.project_config.update({
        'architecture_type': architecture_type,
        'architecture_pattern': architecture_pattern
    })

def render_database_section():
    """데이터베이스 선택 섹션"""
    st.subheader("🗄️ Database Configuration")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        database = st.selectbox(
            "Database Type",
            options=['mysql', 'postgresql', 'h2', 'mariadb'],
            format_func=lambda x: {
                'mysql': '🐬 MySQL',
                'postgresql': '🐘 PostgreSQL',
                'h2': '💾 H2 Database',
                'mariadb': '🦭 MariaDB'
            }[x]
        )
    
    with col2:
        db_info = {
            'mysql': "Popular open-source relational database",
            'postgresql': "Advanced open-source relational database with rich features",
            'h2': "Lightweight in-memory database, perfect for development and testing",
            'mariadb': "MySQL-compatible database with enhanced features"
        }
        st.info(f"💡 {db_info[database]}")
    
    # 세션 상태 업데이트
    st.session_state.project_config['database'] = database

# def render_csv_upload_section():
#     """CSV 파일 업로드 섹션"""
#     st.subheader("📄 CSV Data Upload")
    
#     uploaded_file = st.file_uploader(
#         "Upload CSV file for data modeling",
#         type=['csv'],
#         help="Upload a CSV file to automatically generate entities based on your data structure"
#     )
    
#     if uploaded_file is not None:
#         try:
#             # CSV 파일 읽기
#             df = pd.read_csv(uploaded_file)
            
#             # 파일 정보 표시
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.metric("Rows", len(df))
#             with col2:
#                 st.metric("Columns", len(df.columns))
#             with col3:
#                 st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            
#             # 데이터 미리보기
#             st.write("**Data Preview:**")
#             st.dataframe(df.head(), use_container_width=True)
            
#             # 컬럼 정보 표시
#             st.write("**Column Information:**")
#             column_info = []
#             for col in df.columns:
#                 dtype = str(df[col].dtype)
#                 null_count = df[col].isnull().sum()
#                 column_info.append({
#                     'Column': col,
#                     'Type': dtype,
#                     'Null Count': null_count,
#                     'Sample Value': str(df[col].iloc[0]) if len(df) > 0 else 'N/A'
#                 })
            
#             st.dataframe(pd.DataFrame(column_info), use_container_width=True)
            
#             # 세션 상태에 CSV 데이터 저장
#             st.session_state.project_config['csv_file'] = {
#                 'name': uploaded_file.name,
#                 'data': df.to_dict('records'),
#                 'columns': list(df.columns),
#                 'dtypes': df.dtypes.to_dict()
#             }
            
#         except Exception as e:
#             st.error(f"Error reading CSV file: {str(e)}")
#     else:
#         st.session_state.project_config['csv_file'] = None

def render_additional_requirements_section():
    """추가 요구사항 섹션"""
    st.subheader("📝 Additional Requirements & Entity")
    example = """
    Entity Name,Description,Primary Key,Foreign Keys (Relationships),Key Fields (for quick understanding)
    Users,쇼핑몰의 고객 또는 관리자 정보,id,,email, username, password_hash
    Products,판매되는 상품의 정보,id,category_id (Categories),name, price, stock_quantity
    Categories,상품을 분류하는 카테고리 정보,id,parent_id (Categories - Self-referencing),name
    Orders,고객의 주문 정보,id,user_id (Users),order_date, total_amount, status
    Order_Items,각 주문에 포함된 개별 상품의 상세 정보,id,order_id (Orders),product_id (Products),quantity, price_at_order
    """
    
    additional_requirements = st.text_area(
        "Describe any additional requirements or features:",
        value=st.session_state.project_config['additional_requirements'],
        # placeholder="예시:\n- JWT 인증 구현\n- Redis 캐싱 적용\n- API 문서화 (Swagger)\n- 단위 테스트 포함\n- Docker 컨테이너화",
        placeholder=f"예시:\n{example}",
        height=150
    )
    
    # 세션 상태 업데이트
    st.session_state.project_config['additional_requirements'] = additional_requirements

def render_page1():
    """Page 1: Spring Initializr 스타일 설정 페이지"""
    st.title("🚀 Spring Boot Project Generator")
    st.markdown("Generate your custom Spring Boot project with AI assistance")
    
    # 메인 컨테이너
    with st.container():
        # 왼쪽: 프로젝트 설정
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            render_project_metadata_section()
            st.divider()
            render_project_settings_section()
            st.divider()
            render_additional_requirements_section()
        
        with col_right:
            # 오른쪽: 아키텍처 및 데이터베이스 설정 (Spring Initializr의 dependencies 영역 대체)
            st.markdown("### 🎯 Configuration Panel")
            
            with st.container():
                render_architecture_section()
                st.divider()
                render_database_section()
                # st.divider()
                # render_csv_upload_section()
    
    # 하단 버튼
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔍 Preview Configuration", type="primary", use_container_width=True):
            # 필수 필드 검증
            config = st.session_state.project_config
            if not config['project_name'] or not config['group_id'] or not config['artifact_id'] or not config['package_name']:
                st.error("Please fill in the required fields: Project Name, Group, Artifact and Package Name.")
            else:
                st.session_state.current_page = 'page2'
                st.rerun()

def render_page2():
    """Page 2: 설정 확인 및 프로젝트 생성"""
    st.title("📋 Project Configuration Review")
    
    config = st.session_state.project_config
    
    # 프로젝트 정보 요약
    st.subheader("📊 Project Summary")
    
    # 기본 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Basic Information**")
        st.write(f"• **Project Name:** {config['project_name']}")
        st.write(f"• **Group ID:** {config['group_id']}")
        st.write(f"• **Artifact ID:** {config['artifact_id']}")
        st.write(f"• **Package:** {config['package_name']}")
        st.write(f"• **Description:** {config['description']}")
    
    with col2:
        st.markdown("**⚙️ Technical Configuration**")
        st.write(f"• **Java Version:** {config['java_version']}")
        st.write(f"• **Spring Boot:** {config['spring_boot_version']}")
        st.write(f"• **Packaging:** {config.get('packaging', 'jar').title()}")
    
    # 아키텍처 정보
    st.subheader("🏗️ Architecture & Database")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        arch_icon = "🏢" if config['architecture_type'] == 'monolithic' else "🔗"
        st.markdown(f"**Architecture Type**\n{arch_icon} {config['architecture_type'].title()}")
    
    with col2:
        pattern_icon = "🎯" if config['architecture_pattern'] == 'mvc' else "⬡"
        st.markdown(f"**Architecture Pattern**\n{pattern_icon} {config['architecture_pattern'].upper()}")
    
    with col3:
        db_icons = {'mysql': '🐬', 'postgresql': '🐘', 'h2': '💾', 'mariadb': '🦭'}
        db_icon = db_icons.get(config['database'], '🗄️')
        st.markdown(f"**Database**\n{db_icon} {config['database'].title()}")
    
    # CSV 파일 정보
    # if config['csv_file']:
    #     st.subheader("📄 Uploaded Data")
    #     csv_info = config['csv_file']
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         st.metric("File Name", csv_info['name'])
    #     with col2:
    #         st.metric("Columns", len(csv_info['columns']))
    #     with col3:
    #         st.metric("Rows", len(csv_info['data']))
        
    #     # 컬럼 목록 표시
    #     st.write("**Detected Columns:**")
    #     columns_text = ", ".join(csv_info['columns'])
    #     st.code(columns_text)
    
    # 추가 요구사항
    if config['additional_requirements']:
        st.subheader("📝 Additional Requirements")
        st.text_area(
            "Requirements:",
            value=config['additional_requirements'],
            height=100,
            disabled=True
        )
    
    # 프로젝트 구조 미리보기
    st.subheader("📁 Expected Project Structure")
    package_path = config['package_name'].replace('.', '/')
    # package_path = config['group_id'].replace('.', '/') + '/' + config['package_name'].replace('.', '/')
    
    structure = f"""
    {config['artifact_id']}/
    ├── src/
    │   ├── main/
    │   │   ├── java/
    │   │   │   └── {package_path}/
    │   │   │       ├── {(config['project_name'][:1].upper() + config['project_name'][1:] if config['project_name'] else config['project_name'])}Application.java
    │   │   │       ├── controller/
    │   │   │       ├── service/
    │   │   │       ├── repository/
    │   │   │       ├── entity/
    │   │   │       └── config/
    │   │   └── resources/
    │   │       └──  application.yml
    │   └── test/
    │       └── java/
    ├── build.gradle
    └── README.md
    """
    
    st.code(structure)

    client = AzureOpenAI(
        api_version=OPENAI_API_VERSION,
        azure_endpoint=OPENAI_API_ENDPOINT,
        api_key=OPENAI_API_KEY,
    )

    

    st.title("🧠 LLM 챗봇 데모")
    st.caption("💬 OpenAI GPT 모델을 사용하는 간단한 채팅 앱")

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]

    # 채팅 영역을 스크롤 가능한 컨테이너로 설정
    chat_container = st.container(height=400)  # 높이 약 5cm (400px)
    
    with chat_container:
        # 이전 대화 출력
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 사용자 입력 (컨테이너 밖에 배치하여 항상 하단에 고정)
    user_input = st.chat_input("메시지를 입력하세요...")

    if user_input:
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # OpenAI 응답 요청
        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(
                model= OPENAI_DEPLOYMENT_NAME,
                messages=st.session_state.messages,
                temperature=0.7,
            )
            assistant_reply = response.choices[0].message.content

        # 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        
        # 새 메시지가 추가되면 페이지 새로고침
        st.rerun()
    
    # 하단 버튼
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Configuration", use_container_width=True):
            st.session_state.current_page = 'page1'
            st.rerun()
    
    with col3:
        if st.button("🚀 Generate Project", type="primary", use_container_width=True):
            st.success("🎉 Project generation will be implemented in the next phase!")
            st.balloons()

    
def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(
        page_title="Spring Boot Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 세션 상태 초기화
    init_session_state()
    
    # 현재 페이지에 따라 렌더링
    if st.session_state.current_page == 'page1':
        render_page1()
    elif st.session_state.current_page == 'page2':
        render_page2()

if __name__ == "__main__":
    main()
