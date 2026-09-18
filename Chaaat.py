import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Configuration de l'application
# -------------------------------------------------------------
st.set_page_config(
    page_title="Maroc Explorer Pro | AI Guide",
    page_icon="🇲🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Identifiants de test
USER_CREDENTIALS = {
    "admin": "admin123",
    "visiteur": "maroc2026"
}

# -------------------------------------------------------------
# 2. Initialisation de l'état (Session State)
# -------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Marhaban ! Je suis votre guide virtuel propulsé par l'IA. Quelle région du Maroc souhaitez-vous explorer aujourd'hui ?"}
    ]

# Récupération sécurisée de la clé API
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Initialisation du client global
client = genai.Client(api_key=api_key) if api_key else None

# Initialisation de la session de chat IA (Mémoire)
if client and "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "Tu es un guide touristique expert du Maroc, chaleureux et cultivé. "
                "Tes réponses doivent être structurées, riches en détails historiques et culturels, "
                "et toujours orientées vers le tourisme marocain. Utilise un formatage clair avec des puces si nécessaire."
            ),
            temperature=0.7,
        )
    )

# -------------------------------------------------------------
# 3. Composants d'Interface
# -------------------------------------------------------------
def login_screen():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>🇲🇦 Plateforme Touristique Intelligente</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### 🔐 Authentification")
            with st.form("login_form"):
                user = st.text_input("Identifiant utilisateur")
                pwd = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Initialiser la session", use_container_width=True, type="primary")

                if submit:
                    if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pwd:
                        st.session_state.authenticated = True
                        st.session_state.username = user
                        st.rerun()
                    else:
                        st.error("Échec de l'authentification. Identifiants rejetés.")
        
        st.info("💡 **Accès de test :** `admin` / `admin123`")

def sidebar_menu():
    with st.sidebar:
        st.markdown(f"### 👤 Profil : **{st.session_state.username.capitalize()}**")
        st.caption("🟢 API Gemini Connectée" if api_key else "🔴 API Gemini Déconnectée")
        st.divider()

        st.markdown("#### 🧭 Itinéraires Rapides")
        suggestions = [
            "Élabore un itinéraire de 3 jours à Marrakech.",
            "Quelles sont les spécialités culinaires du Nord ?",
            "Raconte-moi l'histoire de la Mosquée Hassan II."
        ]
        
        for q in suggestions:
            if st.button(q, use_container_width=True):
                process_chat_message(q)
                st.rerun()

        st.divider()
        if st.button("🗑️ Vider la mémoire de l'IA", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Mémoire effacée. Quel est notre nouveau point de départ ?"}]
            # Réinitialisation de la session backend
            if client:
                st.session_state.chat_session = client.chats.create(model="gemini-3.6-flash")
            st.rerun()

        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.rerun()

# -------------------------------------------------------------
# 4. Logique Backend (Interactions API)
# -------------------------------------------------------------
def process_chat_message(prompt: str):
    """Enregistre le prompt, appelle Gemini en conservant le contexte, et stocke la réponse."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not client:
        reply = "⚠️ Erreur système : Clé API Gemini introuvable dans les secrets du serveur."
    else:
        try:
            # Envoi du message à la session (garde l'historique automatiquement)
            response = st.session_state.chat_session.send_message(prompt)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Erreur de communication avec le serveur IA : {e}"
            
    st.session_state.messages.append({"role": "assistant", "content": reply})

def analyze_vision(img: Image.Image):
    """Appel indépendant au modèle pour l'analyse d'image."""
    prompt = (
        "En tant qu'expert du patrimoine marocain, analyse cette image. "
        "1. Identifie le lieu, l'objet ou la scène.\n"
        "2. Fournis un contexte historique ou culturel.\n"
        "3. Liste 3 conseils pratiques pour un touriste découvrant cet élément."
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[prompt, img]
    )
    return response.text

# -------------------------------------------------------------
# 5. Moteur Principal de l'Application
# -------------------------------------------------------------
def main_app():
    sidebar_menu()

    st.title("🇲🇦 Guide Touristique IA & Analyse Multimodale")
    
    if not api_key:
        st.error("Attention : Le backend IA est désactivé. Veuillez configurer `GEMINI_API_KEY` dans `.streamlit/secrets.toml`.")

    tab_chat, tab_vision = st.tabs(["💬 Conversation Contextuelle", "📸 Moteur d'Analyse Visuelle"])

    # --- Onglet 1 : Chabot Contextuel ---
    with tab_chat:
        # Rendu de l'historique UI
        for msg in st.session_state.messages:
            # Choix d'avatars personnalisés
            avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Entrée utilisateur
        if prompt := st.chat_input("Ex: Quel est le meilleur moment pour visiter le désert de Merzouga ?"):
            # Affichage immédiat du message utilisateur
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            # Traitement backend et affichage IA avec spinner
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Analyse de votre requête en cours..."):
                    process_chat_message(prompt)
                    # On affiche le dernier message (la réponse IA)
                    st.markdown(st.session_state.messages[-1]["content"])

    # --- Onglet 2 : Vision par Ordinateur ---
    with tab_vision:
        st.subheader("Identification Automatisée du Patrimoine")
        st.markdown("Soumettez une photographie ; notre modèle IA se charge d'extraire le contexte géographique et historique.")

        uploaded_img = st.file_uploader("Format supporté : JPG, PNG", type=["jpg", "jpeg", "png"])

        if uploaded_img is not None:
            img = Image.open(uploaded_img)
            
            col_img, col_data = st.columns([1, 1.5])
            with col_img:
                st.image(img, caption="Fichier source", use_container_width=True, border=True)
            
            with col_data:
                if st.button("Lancer l'analyse du document visuel", type="primary", use_container_width=True):
                    if not client:
                        st.error("Backend IA indisponible.")
                    else:
                        with st.spinner("Traitement des pixels et extraction sémantique..."):
                            try:
                                result = analyze_vision(img)
                                st.success("Analyse terminée.")
                                st.markdown(result)
                            except Exception as e:
                                st.error(f"Erreur d'exécution du modèle : {e}")

# -------------------------------------------------------------
# Démarrage
# -------------------------------------------------------------
if __name__ == "__main__":
    if not st.session_state.authenticated:
        login_screen()
    else:
        main_app()