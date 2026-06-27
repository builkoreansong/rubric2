import streamlit as st
import re

st.set_page_config(page_title="서·논술형 자동 채점 시스템", layout="wide")

st.title("📝 서·논술형 자동 채점 시스템 (1번 세트: 사회적 촉진과 억제)")
st.markdown("앞서 설계한 **엄격한 채점 기준(루브릭)**을 바탕으로 학생의 답안을 자동 채점합니다.")

# ==========================================
# 1. 채점 기준 및 키워드 사전 정의
# ==========================================
# 유의어 사전 (띄어쓰기 무시를 위해 공백 제거된 패턴)
synonyms = {
    "easy_task": r"(쉬운|단순한|친숙한|노력이덜드는|간단한)",
    "hard_task": r"(어려운|도전적인|복잡한|어려움이있는)",
    "alone": r"(혼자|타인없이|독학|스스로|차분하게|조용한)",
    "together": r"(함께|여럿이|타인이있는|친구들과|같이)",
    "facilitation": r"(사회적촉진|능률이오르|효율이높아|잘되|유리)",
    "inhibition": r"(사회적억제|능률이떨어|방해가되|효율이낮아|불리)"
}

# 설명 방법별 필수 구조 키워드 사전
methods_structure = {
    "비교와 대조": r"(반면|한편|차이|달리|마찬가지로|공통점|지만|하지만)",
    "인과": r"(기때문에|따라서|그러므로|원인|결과로|해서)",
    "정의": r"(은이다|는이다|란|의미는|뜻한다)",
    "예시": r"(예를들어|예컨대|와같은|등이있다)",
    "분석": r"(로구성|요소로|이루어져)",
    "분류와 구분": r"(기준으로나뉜다|종류가있다|구분된다)"
}

# ==========================================
# 2. 자동 채점 로직 함수 정의
# ==========================================
def grade_q1(ans_a, ans_b, ans_c):
    """[서·논술형 1] 빈칸 채우기 채점 (총 3점)"""
    score = 0
    feedback = []
    
    # 띄어쓰기 무시를 위해 학생 답안의 모든 공백 제거
    a_nospace = ans_a.replace(" ", "")
    b_nospace = ans_b.replace(" ", "")
    c_nospace = ans_c.replace(" ", "")
    
    # ㉠ 채점: 쉬운 과제 의미
    if re.search(synonyms["hard_task"], a_nospace):
        feedback.append("❌ ㉠ 오답: 어려운 과제로 오개념을 작성했습니다.")
    elif re.search(synonyms["easy_task"], a_nospace):
        score += 1
        feedback.append("✅ ㉠ 정답: '쉬운 과제'의 의미가 잘 포함되었습니다.")
    else:
        feedback.append("❌ ㉠ 오답: 핵심 의미(비교적 쉬운 과제)가 누락되었습니다.")
        
    # ㉡ 채점: 혼자 집중하는 의미
    if re.search(synonyms["together"], b_nospace):
        feedback.append("❌ ㉡ 오답: '함께'라는 오개념이 포함되었습니다.")
    elif re.search(synonyms["alone"], b_nospace):
        score += 1
        feedback.append("✅ ㉡ 정답: '혼자 차분히 집중함'의 의미가 인정되었습니다.")
    else:
        feedback.append("❌ ㉡ 오답: 핵심 의미(혼자 집중함)가 누락되었습니다.")

    # ㉢ 채점: 사회적 억제 (정확한 용어 혹은 의미)
    if re.search(synonyms["facilitation"], c_nospace):
        feedback.append("❌ ㉢ 오답: '사회적 촉진'과 혼동하였습니다.")
    elif re.search(synonyms["inhibition"], c_nospace):
        score += 1
        feedback.append("✅ ㉢ 정답: '사회적 억제' 개념이 정확합니다.")
    else:
        feedback.append("❌ ㉢ 오답: 핵심 개념(사회적 억제)이 누락되었습니다.")

    return score, feedback

def grade_q2(method1, text1, method2, text2):
    """[서·논술형 2] 설명문 작성 채점 (총 5점)"""
    score = 0
    feedback = []
    
    # 1. 중복 확인 (1점)
    if method1 == method2:
        feedback.append("❌ 요소 2 감점: 서로 다른 두 가지 설명 방법을 사용해야 합니다. (0점 처리)")
        return 0, feedback 
    else:
        score += 1
        feedback.append("✅ 요소 1&2 통과: 두 가지 설명 방법을 중복 없이 제시했습니다. (+1점)")

    # 개별 문장 평가 함수
    def evaluate_sentence(method, text, sent_num):
        s = 0
        f = []
        
        # 띄어쓰기 무시를 위해 학생 답안의 공백 제거
        t_nospace = text.replace(" ", "")
        
        # 구조 일치 여부 확인 (설명 방법 특성 확인)
        if method in methods_structure and re.search(methods_structure[method], t_nospace):
            s += 1
            f.append(f"✅ 문장 {sent_num}: [{method}]의 구조적 특징이 잘 드러납니다. (+1점)")
        else:
            f.append(f"❌ 문장 {sent_num}: [{method}]의 특성(표현)이 문장에 드러나지 않습니다.")

        # 오개념 판별 (기각 조건)
        if re.search(synonyms["easy_task"], t_nospace) and re.search(synonyms["inhibition"], t_nospace):
            f.append(f"❌ 문장 {sent_num} 내용 오류: 쉬운 과제와 사회적 억제를 잘못 연결했습니다.")
            s = 0 
        elif re.search(synonyms["hard_task"], t_nospace) and re.search(synonyms["facilitation"], t_nospace):
            f.append(f"❌ 문장 {sent_num} 내용 오류: 어려운 과제와 사회적 촉진을 잘못 연결했습니다.")
            s = 0
        else:
            # 본문 내용 기반 확인 (결론 방향 확인)
            if re.search(f"{synonyms['easy_task']}|{synonyms['hard_task']}", t_nospace):
                s += 1
                f.append(f"✅ 문장 {sent_num}: 조건에서 요구한 결론(과제 난이도에 따른 방향)이 잘 반영되었습니다. (+1점)")
            else:
                f.append(f"❌ 문장 {sent_num} 내용 오류: 지문에서 요구한 핵심 내용(쉬운/어려운 과제)이 포함되지 않았습니다.")
        return s, f

    s1, f1 = evaluate_sentence(method1, text1, 1)
    s2, f2 = evaluate_sentence(method2, text2, 2)
    
    score += (s1 + s2)
    feedback.extend(f1 + f2)
    
    score = min(score, 5) # 최대 5점 제한
    return score, feedback

# ==========================================
# 3. Streamlit UI 구성
# ==========================================
st.header("학생 답안 입력")

with st.expander("📌 [문항 1] 표 빈칸 채우기 (총 3점)", expanded=True):
    q1_a = st.text_input("㉠ 답안 (정답 예: 비교적 쉬운 취미 생활이나 과제)")
    q1_b = st.text_input("㉡ 답안 (정답 예: 혼자서 차분하게 집중하는 시간)")
    q1_c = st.text_input("㉢ 답안 (정답 예: 사회적 억제)")

with st.expander("📌 [문항 2] 설명문 작성 (총 5점)", expanded=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        m1 = st.selectbox("문장 1 설명 방법", list(methods_structure.keys()), key="m1")
    with col2:
        t1 = st.text_area("문장 1 내용", key="t1")
        
    col3, col4 = st.columns([1, 3])
    with col3:
        m2 = st.selectbox("문장 2 설명 방법", list(methods_structure.keys()), index=1, key="m2")
    with col4:
        t2 = st.text_area("문장 2 내용", key="t2")

if st.button("✅ 채점하기", type="primary"):
    st.markdown("---")
    st.header("📊 채점 결과 및 피드백")
    
    # 문항 1 채점
    st.subheader("[문항 1] 결과")
    score1, fb1 = grade_q1(q1_a, q1_b, q1_c)
    st.write(f"**점수: {score1} / 3 점**")
    for msg in fb1:
        st.write(msg)
        
    # 문항 2 채점
    st.subheader("[문항 2] 결과")
    score2, fb2 = grade_q2(m1, t1, m2, t2)
    st.write(f"**점수: {score2} / 5 점**")
    for msg in fb2:
        st.write(msg)
        
    # 총점
    st.success(f"🏆 총점: {score1 + score2} / 8 점")

AI generated
