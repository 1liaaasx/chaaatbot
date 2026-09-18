import streamlit as st
import nltk
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
# Analyseur d'image sans API (Algorithme Heuristique)
# -------------------------------------------------------------
def analyze_image_colors(image: Image.Image):
    """Analyse les pixels de l'image pour deviner l'ambiance de la destination."""
    # Convertir en RGB et calculer la moyenne des couleurs
    stat = ImageStat.Stat(image.convert("RGB"))
    r, g, b = stat.mean[:3]
    
    # Logique de déduction basée sur les couleurs dominantes
    if b > r and b > g:
        destination = "🌊 **Ambiance Bleue / Côtière**"
        description = "Forte dominante de bleu. Il s'agit très probablement des ruelles de **Chefchaouen**, ou d'une vue sur l'océan à **Essaouira** ou **Agadir**."
    elif r > 140 and g < 130 and b < 100:
        destination = "🏜️ **Ambiance Ocre / Désertique**"
        description = "Forte présence de tons chauds (terre cuite, sable). Cela correspond bien aux remparts de **Marrakech**, aux kasbahs de Ouarzazate, ou aux dunes de **Merzouga**."
    elif g > r and g > b:
        destination = "🌿 **Ambiance Nature / Montagne**"
        description = "Prédominance de vert. Cela évoque les paysages du **Moyen Atlas**, la vallée de l'Ourika ou les cascades d'Ouzoud."
    else:
        destination = "🏛️ **Ambiance Urbaine / Historique**"
        description = "Couleurs mixtes ou neutres. Typique de l'architecture des grandes villes comme **Casablanca**, **Rabat** ou **Fès**."

    return {
        "destination": destination,
        "description": description,
        "rgb": f"Rouge: {int(r)} | Vert: {int(g)} | Bleu: {int(b)}",
        "size": f"{image.width} x {image.height} pixels"
    }

# -------------------------------------------------------------
# Interface de Connexion
# -------------------------------------------------------------
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🇲🇦 Plateforme Touristique</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Connectez-vous pour accéder à votre guide</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            with st.form("login_form"):
                user = st.text_input("Identifiant utilisateur")
                pwd = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter", use_container_width=True, type="primary")

                if submit:
                    if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pwd:
                        st.session_state.authenticated = True
                        st.session_state.username = user
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")
        st.info("💡 **Accès de test :** `admin` / `admin123`")

# -------------------------------------------------------------
# Application Principale
# -------------------------------------------------------------
def main_app():
    # --- Barre latérale ---
    with st.sidebar:
        st.markdown(f"### 👤 Profil : **{st.session_state.username.capitalize()}**")
        st.caption("🟢 Système Actif (Chat + Vision locale)")
        st.divider()

        st.markdown("#### 🧭 Questions Rapides")
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

    # --- Zone Centrale avec Onglets ---
    st.title("🇲🇦 Guide Touristique & Analyseur")
    
    tab_chat, tab_vision = st.tabs(["💬 Guide Interactif", "📸 Analyseur Visuel"])

    # ONGLET 1 : CHATBOT
    with tab_chat:
        st.markdown("Posez vos questions sur les villes, la gastronomie ou le patrimoine marocain.")
        for msg in st.session_state.messages:
            avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Écrivez votre question ici..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            reply = chatbot.respond(prompt)
            if not reply:
                reply = "Désolé, je n'ai pas cette information dans ma base de données. Essayez de me demander des détails sur une ville comme Marrakech ou Agadir !"

            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(reply)

    # ONGLET 2 : VISION SANS API
    with tab_vision:
        st.subheader("Analyseur de photographies de voyage")
        st.caption("Téléversez une photo. L'algorithme analysera les teintes dominantes pour deviner la région marocaine correspondante (sans utiliser d'API externe).")

        uploaded_img = st.file_uploader("Choisissez une image (JPG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_img is not None:
            col_img, col_data = st.columns([1, 1])
            img = Image.open(uploaded_img)

            with col_img:
                st.image(img, caption="Photo importée", use_container_width=True)

            with col_data:
                if st.button("🔍 Lancer l'analyse chromatique", type="primary", use_container_width=True):
                    with st.spinner("Analyse des pixels en cours..."):
                        results = analyze_image_colors(img)
                        st.success("Analyse terminée !")
                        st.markdown(f"### {results['destination']}")
                        st.write(results['description'])
                        
                        st.divider()
                        st.markdown("#### ⚙️ Données Techniques (Backend)")
                        st.code(f"Résolution : {results['size']}\nProfil RGB  : {results['rgb']}")

# -------------------------------------------------------------
# Démarrage
# -------------------------------------------------------------
if __name__ == "__main__":
    if not st.session_state.authenticated:
        login_screen()
    else:
        main_app()
