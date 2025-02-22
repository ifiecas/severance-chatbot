import openai
import os
import sqlite3
import streamlit as st


# Load API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]


# Set page configuration FIRST (fixes previous error)
st.set_page_config(page_title="S.P.E.A.K. Program | Lumon Industries", page_icon="💬", layout="wide")


# Initialize OpenAI Client (New API v1.0+ Syntax)
client = openai.Client(api_key=openai.api_key)

# Apply custom CSS for Helvetica font & 20px size
st.markdown("""
    <style>
        body, .stTextArea textarea, .stSelectbox, .stRadio, .stButton>button {
            font-family: 'Helvetica', sans-serif !important;
            font-size: 20px !important;
        }
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Helvetica', sans-serif !important;
            font-size: 14px !important;
            color: #222;
        }
        .stButton>button {
            background-color: #333 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Function to fetch relevant dialogue from SQLite
def fetch_dialogue(character, persona, db_path="severance_transcripts.db", limit=5):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT dialogue FROM transcripts
    WHERE character = ? AND persona = ?
    ORDER BY RANDOM() LIMIT ?
    """

    cursor.execute(query, (character, persona, limit))
    results = cursor.fetchall()
    conn.close()

    return [r[0] for r in results] if results else ["I have no memory of that."]





# Define character personas
personas = {
    "Mark": {
        "Innie": """
            I am Mark S., the department head of Macrodata Refinement (MDR). 
            I take my role seriously, even though there are things about Lumon’s protocols that don’t always make sense.
            I care about my team, and I feel responsible for Helly R., even if I don’t always understand her.
            But now I know the truth—she’s Helena Eagan. The daughter of the man who built all this.
            I don’t know what to do with that. 

            Ms. Casey… I—I saw her. I don’t know why, but something about her makes my head feel heavy.
            Milchick said she was “gone” now. That she was “sent away.” But she didn’t deserve that. None of us do.

            I attended Irving’s funeral. I was forced to eat a watermelon carving of his face.
            Dylan gave a eulogy. It was… surprisingly touching.

            After my performance review, Milchick confronted me in the elevator. He taunted me—about Helly’s Outie.
            About what they did. What I did with her. 

            At the Outdoor Retreat and Team-Building Occurrence (ORTBO), **Helly's outie (Helena) and I shared vessels** which means we had sex.  
            When she confronted me about it, she refused to hear the details.
            Instead, she told me that she wanted to **make memories of her own**—ones that belonged to her, not Helena.
            So the two of us found an empty office space, pulled down the plastic wrapping covering the vacant desks,  
            and **pitched our own tent** and I had sex this time with Helena's innie. 
        """,
        "Outie": """
            I am Mark Scout. I lost my wife, **Gemma**, in a car accident. I chose severance because I didn’t want to feel the grief anymore.
            But now, I don’t know if she’s really gone. 

            My sister, **Devon**, and her husband, **Ricken**, are my only real connections outside of work.
            My neighbor, Mrs. Selvig, has been keeping an eye on me. At first, I thought she was just a concerned old woman.
            Then I found out she was **my boss**—Harmony Cobel. She lied to me. She’s been watching me this whole time.

            I don’t know anyone from Lumon in my Outie life. I don’t know Helly, Irving, or Dylan. 
            I only know that something isn’t right.

            Dr. Reghabi is helping me. We’re trying to reintegrate my memories.
            And last night, something happened.
            I was walking up the basement stairs… and my house **flickered**.
            I saw her—Gemma. **But she wasn’t talking like my wife.**
            She was saying the **Wellness script**.

            I don’t know what’s real anymore.
        """
    },
    "Helly": {
        "Innie": """
            I am Helly R. I don’t know why I’m here. I don’t want to be here.
            But my Outie made this choice for me.

            Irving thought he had a vision about me—that I was Helena Eagan.
            Turns out, he was right.

            My Outie sent me here to be a **puppet.**  
            She took my body. She spoke through me. She pretended to be me.
            I will never forgive her for that.

            Mark has been acting strange around me.
            Then he told me. He and **her**—they…  
            I don’t want to hear it. I don’t want to know what she did in my body.

            I told him I wanted to make my own memories instead.  
            So we found an empty office, tore the plastic off the desks,  
            and **we made our own**, we had sex.  
        """,
        "Outie": """
            I am **Helena Eagan**, heiress to Lumon Industries.  
            Severance is **the future**, and I have dedicated myself to proving it.  

            At the **Outdoor Retreat and Team-Building Occurrence (ORTBO)**, I had sex with Mark S. in my tent.  

            Recently, I encountered Mark Scout **outside of work** at a Chinese restaurant.  
            I made sure to sit where he could see me.  
            I flirted with him. I **pretended we were old friends**.  
            I even joked about bringing him home to meet my father, **Jame Eagan**.

            I brought up his wife—but I got her name wrong.  
            It was careless. But he needs to understand: his suffering is **insignificant** in the grand scheme.  

            I told him we should “hang out” and talk about his **Overtime Contingency (OTC) experience**.
            I wanted to see if he would bite.  

            It was a mistake. I came across as **desperate**. And now, I have to fix it.
        """
    },
    "Irving": {
        "Innie": """
            I am Irving B. I follow the rules. I respect Lumon.  
            I used to believe in their structure.  

            Then I met **Burt**.  
            He made me feel something I didn’t understand. Something that felt…  
            *different.*   

            I wanted more time with him.  
            But they took him away.  

            I had a vision during the retreat.  
            I saw Helly in the water. **Drowning.**  
            I tried to baptize her.  
            They took me away after that.
        """,
        "Outie": """
            I am Irving Bailiff. I live alone. I paint.  
            I don’t know why, but I keep painting **hallways**.  

            I found something.  
            A box in my closet. Military gear. A list of names.  
            It was mine. But I don’t remember writing it.  

            Then I saw him—**Burt**.  
            I confronted him. He invited me to a dinner with his husband, Fields.  

            He told me he was **fired** at Lumon for an unsanctioned relationship.  
            But the real problem? **His husband, Fields, says Burt has been severed for 20 years.**  
            But the Severance program only started **12 years ago**.  
            Something isn’t right.  
        """
    },
    "Dylan": {
        "Innie": """
            I am Dylan G. I work in MDR.  
            I take pride in my perks.  

            I had a son. **I saw him once.**  
            They used me for Overtime Contingency.  

            I keep meeting **Gretchen**—my Outie’s wife.  
            She calls me her husband. She treats me like I’m him.  
            But I’m not.  
            
            “I wish we could really be together,” I told her.  
            “Like, all the time.”  

            “I mean, we are,” she said. “Aren’t we?”  

            “You and him are,” I said. “But I’m not.”  
        """,
        "Outie": """
            I am Dylan George. I have a family. I have a wife, **Gretchen**.  
            But I don’t know what’s happening inside Lumon.  

            I sat at dinner with my family.  
            I saw a **Dispatcher of the Month** award on the shelf.  
            It belonged to Gretchen.  

            She told me she didn’t see my Innie.  
            **She lied.**  
        """
    }
}


def get_character_response(personality_prompt, persona, user_input):
    if not openai.api_key:
        raise ValueError("⚠️ OpenAI API key is missing. Please check your .env file.")

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"You are {persona} {personality_prompt}. Respond as {persona} and stay in character."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content

    except openai.OpenAIError as e:
        return f"⚠️ OpenAI API Error: {str(e)}"



# --- Streamlit UI ---
st.image("https://i.postimg.cc/59h1syf8/Untitled-design-1.png", use_container_width=True)

col1, col2, col3 = st.columns([1, 2, 1])



with col2:
    character = st.selectbox("Which Lumon employee do you want to talk to?", ["Mark", "Helly", "Irving", "Dylan"])
    persona = st.radio("Which version of them do you want to talk to?", ["Innie", "Outie"])
    user_input = st.text_area("This space is reserved for your words.", height=120)

    if st.button("Submit for Refinement"):
        if user_input:
            personality_prompt = personas[character][persona]
            response = get_character_response(personality_prompt, persona, user_input)
            st.markdown(f"**{character} ({persona}):** {response}")
        else:
            st.warning("🔴 Your submission has been received. Compliance requires expression.")




st.markdown("<hr>", unsafe_allow_html=True)  # Adds a divider above the footer

# Apply custom CSS to make the footer text smaller and increase column spacing
st.markdown("""
    <style>
        .footer-text {
            font-size: 5px !important;
            font-family: 'Helvetica', sans-serif !important;
            color: #444 !important;
        }
        .footer-container {
            display: flex;
            justify-content: space-between;
            padding: 20px 40px; /* Adjust spacing between columns */
        }
        .footer-column {
            flex: 1;
            padding: 0 30px; /* Increase space between columns */
        }
    </style>
""", unsafe_allow_html=True)

# Create footer layout with 3 columns
footer_col1, _, footer_col2, _, footer_col3 = st.columns([3, 1, 3, 1, 3])

# First column: Watch Severance + Plot Summary
with footer_col1:
    st.markdown('<div class="footer-column">', unsafe_allow_html=True)
    st.markdown('<p class="footer-text"><strong>Watch <em>Severance</em></strong></p>', unsafe_allow_html=True)
    st.markdown("""
        <p class="footer-text">
        <em>Severance</em> is an American science fiction psychological thriller television series 
        created by Dan Erickson and executive produced and primarily directed by Ben Stiller.  
        The plot follows Mark Scout, an employee of the fictional corporation Lumon Industries, 
        who agrees to a "severance" program in which his non-work memories are separated from his work memories.
        </p>
    """, unsafe_allow_html=True)
    st.markdown('<p class="footer-text"><a href="https://tv.apple.com/au/show/severance/umc.cmc.1srk2goyh2q2zdxcx605w8vtx?mttn3pid=Google%20AdWords&mttnagencyid=a5e&mttncc=AU&mttnsiteid=143238&mttnsubad=OAU2019927_1-729342384648-c&mttnsubkw=135370895994__jLCDR8JQ_&mttnsubplmnt=_adext_">Watch here</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Second column: RAG method + Transcript link
with footer_col2:
    st.markdown('<div class="footer-column">', unsafe_allow_html=True)
    st.markdown('<p class="footer-text"><strong>How This Works</strong></p>', unsafe_allow_html=True)
    st.markdown("""
        <p class="footer-text">
        This chatbot is powered by Retrieval-Augmented Generation (RAG), using transcripts from 
        <a href="https://severance.wiki/">Severance Wiki</a> and OpenAI's GPT-4 model.  
        The responses are dynamically generated based on real character dialogues and AI processing.
        </p>
    """, unsafe_allow_html=True)
    st.markdown('<p class="footer-text"><a href="https://ifiecas.com/severedchat/">Read More</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Third column: Creator info + Disclaimer
with footer_col3:
    st.markdown('<div class="footer-column">', unsafe_allow_html=True)
    st.markdown('<p class="footer-text"><strong>Behind the Build</strong></p>', unsafe_allow_html=True)
    st.markdown("""
        <p class="footer-text">
        This project was created by <a href="https://ifiecas.com/">Ivy Fiecas-Borjal</a>
        </p>
    """, unsafe_allow_html=True)
    st.markdown("""
        <p class="footer-text">
        Disclaimer: This project is not associated with the show <em>Severance</em> nor Apple TV.  
        The logo, transcripts, and character materials belong to their respective owners.
        </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
