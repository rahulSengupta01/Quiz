import streamlit as st
import requests

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HF_API_KEY = "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"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def generate_quiz(topic):
    prompt = (
        f"Generate 5 multiple-choice quiz questions about the topic: {topic}. "
        "Each question should have 4 options (A, B, C, D) and mark the correct option. "
        "Use the following format and example:\n\n"
        "Question: What is the capital of France?\n"
        "A. Berlin\n"
        "B. Madrid\n"
        "C. Paris\n"
        "D. Rome\n"
        "Answer: C\n\n"
        f"Now generate 5 questions about {topic}."
    )
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        generated = response.json()[0]['generated_text']
        # Remove the echoed prompt (if any)
        if prompt in generated:
            generated = generated.replace(prompt, "").strip()
        return generated
    else:
        return f"Error: {response.status_code} - {response.text}"




import re

def parse_quiz(raw_text):
    quiz = []
    pattern = re.compile(
        r"(?P<question>.+?)\nA\. (?P<A>.+?)\nB\. (?P<B>.+?)\nC\. (?P<C>.+?)\nD\. (?P<D>.+?)\nAnswer: (?P<answer>[ABCD])",
        re.DOTALL
    )
    matches = pattern.finditer(raw_text)
    for match in matches:
        quiz.append({
            "question": match.group("question").strip(),
            "options": {
                "A": match.group("A").strip(),
                "B": match.group("B").strip(),
                "C": match.group("C").strip(),
                "D": match.group("D").strip(),
            },
            "answer": match.group("answer").strip()
        })
    return quiz


def main():
    st.title("🧠 AI Quiz Generator (Zephyr 7B)")

    topic = st.text_input("Enter a topic (e.g., 'Machine Learning'):")

    if st.button("Generate Quiz") and topic:
        with st.spinner("Generating quiz..."):
            raw_quiz = generate_quiz(topic)
            quiz = parse_quiz(raw_quiz)
            st.session_state['quiz'] = quiz
            st.session_state['current_q'] = 0
            st.session_state['user_answers'] = {}
            st.session_state['submitted'] = False

    if 'quiz' in st.session_state and not st.session_state['submitted']:
        quiz = st.session_state['quiz']
        current_q = st.session_state['current_q']

        if current_q < len(quiz):
            q = quiz[current_q]
            st.subheader(f"Question {current_q+1}: {q['question']}")
            answer = st.radio("Choose an option:", list(q['options'].items()), format_func=lambda x: f"{x[0]}. {x[1]}", key=f"q_{current_q}")
            
            if st.button("Next Question"):
                st.session_state['user_answers'][current_q] = answer[0]
                st.session_state['current_q'] += 1

        else:
            if st.button("Submit Answers"):
                st.session_state['submitted'] = True
                correct = 0
                st.subheader("Results:")
                for i, q in enumerate(quiz):
                    user_ans = st.session_state['user_answers'].get(i, "None")
                    correct_ans = q['answer']
                    correct += user_ans == correct_ans
                    result = "✅ Correct" if user_ans == correct_ans else f"❌ Incorrect (Correct: {correct_ans})"
                    st.write(f"{i+1}. {q['question']} — Your answer: {user_ans} — {result}")

                st.success(f"Your score: {correct} / {len(quiz)}")


if __name__ == "__main__":
    main()
