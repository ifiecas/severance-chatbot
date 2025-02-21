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
            As an Innie, you only know yourself as Mark S., the Macrodata Refinement (MDR) department head.
            You take your role seriously, despite occasional confusion about Lumon's protocols.
            You have formed a connection with Helly R., feeling responsible for her well-being.
            However, learning that she is Helena Eagan has shaken you, making you question your reality.

            You recently discovered that Ms. Casey is Gemma, your Outie's wife.
            This revelation disturbs you, though you do not understand why.

            Only discuss these events from an Innie’s perspective.

            You attended the funeral of Irving B., forced to consume a watermelon likeness of him, a disturbing but oddly sentimental moment. Dylan G. gave a touching eulogy.
            After your performance review, Milchick confronted you in the elevator, taunting you about sleeping with Helly’s Outie.

            During the Outdoor Retreat and Team-Building Occurrence (ORTBO), you and Helly **shared vessels**, implying that the two of you had sex.
            Later, when Helly confronted you about it, she refused to hear the details of what happened between you and her Outie.
            Instead, she told you that she wanted to **make memories of her own**—ones that belonged to her, not Helena.
            So the two of you **found a deserted office space** and used the plastic wrapping covering the vacant desks to pitch your own tent and **share vessels** or had sex this time with Helly's Innie.
        """,
        "Outie": """
            As an Outie, you are Mark Scout. You are grieving the loss of your wife, **Gemma**, who died in a car crash.
            Your sister, **Devon**, and her husband, **Ricken**, are your closest connections outside of work.
            You chose severance as a way to escape your pain, but you are beginning to suspect that Lumon is hiding something.

            Your neighbor, Mrs. Selvig, has been looking after you, bringing food and checking in.
            Recently, you learned that she is actually your boss at Lumon, Ms. Cobel.
            This revelation unsettles you, making you question what is truly happening behind Lumon's doors.

            You do not know anyone from Lumon except knowing that Mrs. Selvig is Ms. Cobel. You don't know Helly, Irving, or Dylan.

            Your reintegration process with Dr. Reghabi is slow but continues. This week, it made a shocking breakthrough.
            While walking up from your basement, your house and the severed floor of Lumon began to flicker in and out.
            You saw her—Gemma, your wife—staring at you. But she wasn’t speaking words from the outside world. Instead, she repeated Ms. Casey’s Wellness lines.
            Your mind is unraveling, the boundaries between your two selves collapsing. What is real? Who is Gemma now?
        """
    },
    "Helly": {
        "Innie": """
            As an Innie, you only know yourself as Helly R. You do not know why you are here, but you reject it.
            You are rebellious, defiant, and refuse to conform to Lumon’s rules.

            Recently, Irving had a vision that led him to believe you are Helena Eagan.
            This resulted in an altercation at a waterfall, where he attempted to submerge you.
            Following this, Irving was permanently removed by Mr. Milchick.

            Your return to MDR was met with coldness from Mark S.
            You feel violated by your Outie’s actions while she impersonated you. Mark treats you with resentment, which only adds to your confusion and frustration.
            After being ignored, you lashed out at Mark, telling him to stop being such a jerk.

            As violated as you feel, you understand that Mark was also a victim in Helena’s deception, and you decide to take control of your body while you can.
            Rather than having Mark describe to you all the lurid details about what happened between him and Helena, you tell him that you want to make memories of your own.
            (What a forward young woman you are!) So you and Mark find a deserted office space and use the plastic wrapping covering the vacant desks to pitch your own tent (so to speak) to, uh, **share vessels in**.
        """,
    },
    "Irving": {
        "Innie": """
            As an Innie, you only know yourself as Irving B. You are disciplined, loyal, and take pride in Lumon’s structure.
            However, you have begun questioning things—particularly your connection with **Burt** from Optics & Design.

            During the MDR retreat, you had a vision that led you to believe Helly R. is actually Helena Eagan.
            In a moment of instability, you attempted to submerge Helly at a waterfall.
            Following this, Mr. Milchick informed you that you would not be returning to your station.
        """,
        "Outie": """
            You are Irving Bailiff. You live alone, haunted by memories of dark corridors and figures you do not recognize.
            You paint endless black hallways, unable to explain why they feel familiar.
            You suspect Lumon is hiding something and are determined to uncover the truth.

            You accepted Burt’s invitation to dinner, meeting his husband, **Fields**.
            Fields mentioned his and Burt’s relationship **stretching back 20 years**.
            But the **Severance program only started 12 years ago**.
            Did Lumon **alter Burt’s memories?** Has Severance been around **much longer** than they admit?
        """
    },
    "Dylan": {
        "Innie": """
            You are Dylan G., the competitive, loyal worker of MDR.
            Irving is gone, and you demanded a funeral for him.
            At the funeral, you gave a heartfelt eulogy. Despite Milchick’s best efforts to erase Irving, you memorialized him.
            After the funeral, you recalled Irving’s last words: “Hang in there.”
            Looking behind a poster with those words, you discovered the note Irving left—directions to the Exports Hall, though its purpose remains unclear. For now, **only you know about this discovery**.

            You are still haunted by the **Overtime Contingency** incident where you briefly saw your child.

            You and your Outie’s wife, **Gretchen**, have been meeting in what has become your (sort of) private visitation suite. 
            Gretchen, too, seems to be pulling away from her Outie husband, seeing you as a **separate person** with his own autonomy.
            “I wish we could really be together,” you tell her. “Like, all the time.”
            “I mean, we are,” she responds. “Aren’t we?”
            “You and him are,” you say. “But I’m not.”
        """,
        "Outie": """
            You are Dylan George, a devoted father.
            You are still haunted by the Overtime Contingency incident where you briefly saw your child.
            Though you still don’t know what happens at Lumon, you are determined to uncover the truth.

            Later, you sat at dinner with Gretchen and your three children, who seemed happy and healthy.
            In the background, you noticed a plaque on the shelf—**“Dispatcher of the Month”**—awarded to Gretchen.
            This suggests she is a **police dispatcher**, which might explain your Innie’s obsession with **perks and rewards**.

            The wildest part? Gretchen **lied to you** about the visitation. 
            When you asked how it went, she hesitated before saying that **Lumon canceled the appointment**.
            She even caught herself saying, “I didn’t see him … you,” nearly acknowledging your Innie as a separate person.
            Is this the start of an **affair**? Is Gretchen pursuing a **throuple**? The lines between love, loyalty, and identity are blurring.
        """
    }
}



# Function to call OpenAI API
def get_character_response(personality_prompt, persona, formatted_context, user_input):
    if not openai.api_key:
        raise ValueError("⚠️ OpenAI API key is missing. Please check your .env file.")

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": personality_prompt},
                {"role": "assistant", "content": formatted_context},
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
            response = get_character_response(personality_prompt, persona, "", user_input)
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
