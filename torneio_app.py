
import streamlit as st
import sqlite3
import random
import os

conn = sqlite3.connect("torneio.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS times (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    emblema TEXT,
    nivel INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ligas (
    id INTEGER PRIMARY KEY,
    nome TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ligas_times (
    liga_id INTEGER,
    time_id INTEGER
)
""")

conn.commit()

st.set_page_config(page_title="Gerenciador de Torneios de Futebol", layout="centered")
st.title("⚽ Gerenciador de Torneios de Futebol")

menu = ["Cadastrar Time", "Criar Liga", "Adicionar Time na Liga", "Simular Partida"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastrar Time":
    st.header("Adicionar Time")
    nome = st.text_input("Nome do Time")
    nivel = st.slider("Nível do Time (1-100)", 1, 100)
    emblema = st.file_uploader("Emblema do Time (opcional)", type=["png", "jpg", "jpeg"])

    if st.button("Adicionar Time"):
        emblema_path = ""
        if emblema:
            emblema_path = f"emblemas/{emblema.name}"
            os.makedirs("emblemas", exist_ok=True)
            with open(emblema_path, "wb") as f:
                f.write(emblema.getbuffer())

        cursor.execute("INSERT INTO times (nome, emblema, nivel) VALUES (?, ?, ?)", (nome, emblema_path, nivel))
        conn.commit()
        st.success("Time adicionado com sucesso!")

    st.subheader("Times Cadastrados")
    times = cursor.execute("SELECT nome, nivel, emblema FROM times").fetchall()
    for t in times:
        st.write(f"{t[0]} (Nível: {t[1]})")
        if t[2]:
            st.image(t[2], width=100)

elif choice == "Criar Liga":
    st.header("Criar Nova Liga")
    nome_liga = st.text_input("Nome da Liga")

    if st.button("Criar Liga"):
        cursor.execute("INSERT INTO ligas (nome) VALUES (?)", (nome_liga,))
        conn.commit()
        st.success("Liga criada com sucesso!")

    st.subheader("Ligas Criadas")
    ligas = cursor.execute("SELECT nome FROM ligas").fetchall()
    for l in ligas:
        st.write(f"🏆 {l[0]}")

elif choice == "Adicionar Time na Liga":
    st.header("Adicionar Time em Liga")

    ligas = cursor.execute("SELECT id, nome FROM ligas").fetchall()
    times = cursor.execute("SELECT id, nome FROM times").fetchall()

    liga_nome = st.selectbox("Escolha a Liga", [f"{l[0]} - {l[1]}" for l in ligas])
    time_nome = st.selectbox("Escolha o Time", [f"{t[0]} - {t[1]}" for t in times])

    if st.button("Adicionar na Liga"):
        liga_id = int(liga_nome.split(" - ")[0])
        time_id = int(time_nome.split(" - ")[0])

        cursor.execute("INSERT INTO ligas_times (liga_id, time_id) VALUES (?, ?)", (liga_id, time_id))
        conn.commit()
        st.success("Time adicionado à liga com sucesso!")

elif choice == "Simular Partida":
    st.header("Simular Partida Aleatória")
    times = cursor.execute("SELECT nome, nivel FROM times").fetchall()

    if len(times) < 2:
        st.warning("Cadastre pelo menos dois times para simular uma partida.")
    else:
        if st.button("Simular"):
            time1, time2 = random.sample(times, 2)
            resultado1 = random.randint(0, int(time1[1]) // 10 + 2)
            resultado2 = random.randint(0, int(time2[1]) // 10 + 2)

            st.subheader("Resultado da Partida")
            st.write(f"{time1[0]} {resultado1} x {resultado2} {time2[0]}")
