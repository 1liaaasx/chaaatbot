import streamlit as st
import nltk

# Téléchargement défensif pour Streamlit Cloud
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

from nltk.chat.util import Chat, reflections
from PIL import Image, ImageStat

# -------------------------------------------------------------
# Configuration de l'interface
# -------------------------------------------------------------
st.set_page_config(
    page_title="Maroc Explorer Pro",
    page_icon="🇲🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# Feuilles de styles CSS personnalisées
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #b91c1c 0%, #c2410c 50%, #d97706 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(185, 28, 28, 0.2);
    }
    .main-header h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.3rem;
        color: #ffffff;
    }
    .main-header p {
        margin: 0.6rem 0 0 0;
        font-size: 1.05rem;
        opacity: 0.95;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding-bottom: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 0 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [aria-selected="true"] {
        background-color: #b91c1c !important;
        color: white !important;
        border-color: #b91c1c !important;
        box-shadow: 0 4px 15px rgba(185, 28, 28, 0.35);
    }

    div[data-testid="stSidebarHeader"] {
        padding-bottom: 0rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: rgba(16, 185, 129, 0.12);
        color: #10b981;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 1.1rem;
        margin-bottom: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .result-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 14px;
        padding: 1.4rem;
        border: 1px solid rgba(255, 255, 255, 0.09);
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Base de connaissances (NLTK Pairs)
# -------------------------------------------------------------
pairs = [
    [r"mon nom est (.*)", ["Enchanté %1 ! Je suis votre guide virtuel. Prêt à explorer le Maroc ?"]],
    [r"bonjour|salut|coucou|salam", [
        "Salam ! Prêt à découvrir les merveilles du Maroc ?",
        "Bonjour ! Quelle destination marocaine t'intéresse aujourd'hui ?"
    ]],
    [r"(.*)capitale(.*)", ["La capitale administrative et politique du Maroc est Rabat."]],
    [r"(.*)marrakech(.*)", ["Marrakech, la ville ocre ! Célèbre pour sa médina, la place Jemaa el-Fna et ses souks."]],
    [r"(.*)casablanca(.*)", ["Casablanca est la capitale économique du pays, réputée pour sa majestueuse Mosquée Hassan II."]],
    [r"(.*)chefchaouen(.*)", ["Chefchaouen, la perle bleue nichée dans les montagnes du Rif, idéale pour des balades relaxantes."]],
    [r"(.*)agadir(.*)", ["Agadir est parfaite pour le soleil toute l'année, sa corniche animée et ses spots de surf."]],
    [r"(.*)safi(.*)", ["Safi est renommée pour sa poterie artisanale, sa colline des potiers et son passé atlantique."]],
    [r"(.*)essaouira(.*)", ["Essaouira (l'ancienne Mogador) séduit par ses remparts maritimes et son vent parfait pour le kitesurf."]],
    [r"(.*)monument(.*)", ["Parmi les incontournables : la Mosquée Hassan II, la Koutoubia à Marrakech, la Tour Hassan à Rabat."]],
    [r"(.*)desert(.*)", ["Le désert marocain offre des paysages féeriques, notamment les dunes de Merzouga et de Zagora."]],
    [r"(.*)montagne(.*)", ["Le Maroc abrite de superbes massifs : le Haut Atlas (mont Toubkal), le Moyen Atlas et le Rif."]],
    [r"(.*)cuisine(.*)|(.*)manger(.*)|(.*)plat(.*)", ["La gastronomie marocaine est un régal : couscous, tajines, pastilla, et thé à la menthe."]],
    [r"(.*)meilleure destination(.*)", ["Tout dépend de tes envies : Marrakech pour l'ambiance, Agadir pour la mer, Merzouga pour le désert."]],
    [r"merci(.*)", ["Avec grand plaisir ! N'hésite pas si tu as d'autres questions. 🇲🇦"]],
    [r"au revoir|bye|quitter", ["Au revoir et excellent séjour au Maroc !"]],
    [r"(.*)", ["Je ne suis pas sûr de saisir. Pose-moi une question sur une ville ou un monument marocain !"]]
]

chatbot = Chat(pairs, reflections)

# -------------------------------------------------------------
# Gestion de l'état (Session State)
# -------------------------------------------------------------
USER_CREDENTIALS = {"admin": "admin123", "visiteur": "maroc2026"}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Marhaban ! Je suis votre guide virtuel. Que souhaitez-vous découvrir au Maroc ?"}
    ]

# -------------------------------------------------------------
# Analyseur d'image sans API
# -------------------------------------------------------------
def analyze_image_colors(image: Image.Image):
    stat = ImageStat.Stat(image.convert("RGB"))
    r, g, b = stat.mean[:3]

    if b > r and b > g:
        destination = "🌊 Ambiance Bleue / Côtière"
        description = "Forte dominante de bleu. Il s'agit très probablement des ruelles de **Chefchaouen**, ou d'une vue sur l'océan à **Essaouira** ou **Agadir**."
    elif r > 140 and g < 130 and b < 100:
        destination = "🏜️ Ambiance Ocre / Désertique"
        description = "Forte présence de tons chauds (terre cuite, sable). Cela correspond bien aux remparts de **Marrakech**, aux kasbahs de Ouarzazate, ou aux dunes de **Merzouga**."
    elif g > r and g > b:
        destination = "🌿 Ambiance Nature / Montagne"
        description = "Prédominance de vert. Cela évoque les paysages du **Moyen Atlas**, la vallée de l'Ourika ou les cascades d'Ouzoud."
    else:
        destination = "🏛️ Ambiance Urbaine / Historique"
        description = "Couleurs mixtes ou neutres. Typique de l'architecture des grandes villes comme **Casablanca**, **Rabat** ou **Fès**."

    return {
        "destination": destination,
        "description": description,
        "r": int(r),
        "g": int(g),
        "b": int(b),
        "size": f"{image.width} × {image.height} px"
    }

# -------------------------------------------------------------
# Interface de Connexion
# -------------------------------------------------------------
def login_screen():
    st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <span style="font-size: 3.5rem;">🇲🇦</span>
            <h1 style="margin: 0.4rem 0 0.2rem 0; font-weight: 700;">Maroc Explorer Pro</h1>
            <p style="color: #9ca3af; font-size: 0.95rem;">Plateforme Touristique Intelligente</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### Connexion voyageur")
            with st.form("login_form"):
                user = st.text_input("Identifiant utilisateur", placeholder="ex: admin ou visiteur")
                pwd = st.text_input("Mot de passe", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Se connecter à la session", use_container_width=True, type="primary")

                if submit:
                    if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pwd:
                        st.session_state.authenticated = True
                        st.session_state.username = user
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 0.9rem; margin-top: 1rem; text-align: center;">
            <span style="font-size: 0.85rem; color: #9ca3af;">
                💡 <b>Accès rapides :</b> <code>admin</code> / <code>admin123</code> &nbsp;|&nbsp; <code>visiteur</code> / <code>maroc2026</code>
            </span>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Application Principale
# -------------------------------------------------------------
def main_app():
    # --- Barre latérale ---
    with st.sidebar:
        st.markdown(f"### 👋 Bonjour, **{st.session_state.username.capitalize()}**")
        st.markdown('<div class="status-badge">● Module NLTK & Vision Actif</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown("##### 🧭 Questions Rapides")
        suggestions = [
            "Que faire à Marrakech ?",
            "Parle-moi de Casablanca",
            "Quels sont les plats typiques ?",
            "Parle-moi du désert"
        ]

        for q in suggestions:
            if st.button(q, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.session_state.messages.append({"role": "assistant", "content": chatbot.respond(q)})
                st.rerun()

        st.divider()
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Historique réinitialisé ! Où partons-nous ?"}]
            st.rerun()

        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.rerun()

    # --- En-tête principal stylisé ---
    st.markdown("""
    <div class="main-header">
        <h1>🇲🇦 Maroc Explorer Pro</h1>
        <p>Votre assistant de voyage interactif et analyseur d'ambiance visuelle marocaine.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_chat, tab_vision = st.tabs(["💬 Guide Touristique Interactif", "📸 Analyseur d'Image & Chromatique"])

    # --- ONGLET 1 : CHATBOT ---
    with tab_chat:
        for msg in st.session_state.messages:
            avatar = "🧑‍💻" if msg["role"] == "user" else "🕌"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Posez votre question sur les villes, monuments ou circuits..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            reply = chatbot.respond(prompt)
            if not reply:
                reply = "Désolé, je n'ai pas cette information dans ma base de données. Essayez de me poser une question sur Marrakech, Agadir ou Chefchaouen !"

            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant", avatar="🕌"):
                st.markdown(reply)

    # --- ONGLET 2 : VISION ---
    with tab_vision:
        st.markdown("#### Détection d'Ambiance Géographique")
        st.caption("Téléversez un cliché touristique pour analyser le profil colorimétrique et déduire la région marocaine.")

        uploaded_img = st.file_uploader("Importer une photo de voyage (JPG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_img is not None:
            col_img, col_data = st.columns([1.1, 1.3], gap="large")
            img = Image.open(uploaded_img)

            with col_img:
                with st.container(border=True):
                    st.image(img, caption="Photographie importée", use_container_width=True)

            with col_data:
                if st.button("🔍 Lancer le diagnostic visuel", type="primary", use_container_width=True):
                    with st.spinner("Extraction des canaux chromatiques..."):
                        results = analyze_image_colors(img)

                        st.markdown(f"""
                        <div class="result-card">
                            <h3 style="margin: 0 0 0.5rem 0; color: #f59e0b;">{results['destination']}</h3>
                            <p style="margin: 0; font-size: 1rem; line-height: 1.5;">{results['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                        st.markdown("##### Métriques de l'image")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Canal Rouge", f"{results['r']}")
                        m2.metric("Canal Vert", f"{results['g']}")
                        m3.metric("Canal Bleu", f"{results['b']}")
                        m4.metric("Format", results['size'])

# -------------------------------------------------------------
# Démarrage
# -------------------------------------------------------------
if __name__ == "__main__":
    if not st.session_state.authenticated:
        login_screen()
    else:
        main_app()
