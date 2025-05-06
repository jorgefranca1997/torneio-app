
import streamlit as st
import sqlite3
import random
import os
from datetime import datetime

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY,
    liga_id INTEGER,
    time1 TEXT,
    time2 TEXT,
    gols1 INTEGER,
    gols2 INTEGER,
    data TEXT
)
""")

conn.commit()

st.set_page_config(page_title="Torneio de Futebol", layout="wide")
st.title("🏆 Gerenciador de Torneios de Futebol - V2")

menu = ["Cadastrar Time", "Criar Liga", "Adicionar Time na Liga", "Simular Partida", "Tabela da Liga"]
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
    st.header("Simular Partida Aleatória da Liga")

    ligas = cursor.execute("SELECT id, nome FROM ligas").fetchall()
    liga_nome = st.selectbox("Escolha a Liga", [f"{l[0]} - {l[1]}" for l in ligas])
    liga_id = int(liga_nome.split(" - ")[0])

    times = cursor.execute("SELECT times.nome, times.nivel FROM ligas_times JOIN times ON ligas_times.time_id = times.id WHERE ligas_times.liga_id = ?", (liga_id,)).fetchall()

    if len(times) < 2:
        st.warning("Adicione pelo menos dois times na liga para simular partidas.")
    else:
        if st.button("Simular Partida"):
            time1, time2 = random.sample(times, 2)
            resultado1 = random.randint(0, int(time1[1]) // 10 + 3)
            resultado2 = random.randint(0, int(time2[1]) // 10 + 3)

            cursor.execute("INSERT INTO partidas (liga_id, time1, time2, gols1, gols2, data) VALUES (?, ?, ?, ?, ?, ?)",
                           (liga_id, time1[0], time2[0], resultado1, resultado2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

            st.success(f"{time1[0]} {resultado1} x {resultado2} {time2[0]}")

    st.subheader("Últimas Partidas")
    partidas = cursor.execute("SELECT time1, gols1, gols2, time2, data FROM partidas WHERE liga_id = ? ORDER BY id DESC", (liga_id,)).fetchall()
    for p in partidas:
        st.write(f"{p[0]} {p[1]} x {p[2]} {p[3]} ({p[4]})")

elif choice == "Tabela da Liga":
    st.header("Tabela de Classificação da Liga")

    ligas = cursor.execute("SELECT id, nome FROM ligas").fetchall()
    liga_nome = st.selectbox("Escolha a Liga", [f"{l[0]} - {l[1]}" for l in ligas])
    liga_id = int(liga_nome.split(" - ")[0])

    times = cursor.execute("SELECT times.nome FROM ligas_times JOIN times ON ligas_times.time_id = times.id WHERE ligas_times.liga_id = ?", (liga_id,)).fetchall()
    tabela = {t[0]: {"P": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0, "SG": 0} for t in times}

    partidas = cursor.execute("SELECT time1, gols1, gols2, time2 FROM partidas WHERE liga_id = ?", (liga_id,)).fetchall()

    for p in partidas:
        t1, g1, g2, t2 = p
        tabela[t1]["GP"] += g1
        tabela[t1]["GC"] += g2
        tabela[t2]["GP"] += g2
        tabela[t2]["GC"] += g1

        if g1 > g2:
            tabela[t1]["V"] += 1
            tabela[t2]["D"] += 1
            tabela[t1]["P"] += 3
        elif g1 < g2:
            tabela[t2]["V"] += 1
            tabela[t1]["D"] += 1
            tabela[t2]["P"] += 3
        else:
            tabela[t1]["E"] += 1
            tabela[t2]["E"] += 1
            tabela[t1]["P"] += 1
            tabela[t2]["P"] += 1

    for time in tabela:
        tabela[time]["SG"] = tabela[time]["GP"] - tabela[time]["GC"]

    st.subheader("Classificação Atual")
    tabela_ordenada = sorted(tabela.items(), key=lambda x: (x[1]["P"], x[1]["SG"]), reverse=True)
    st.table([{**{"Time": t[0]}, **t[1]} for t in tabela_ordenada])
