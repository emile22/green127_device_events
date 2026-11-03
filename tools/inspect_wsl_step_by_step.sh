#!/usr/bin/env bash

# ============================================================
# WSL / Ubuntu inspection script
# Objectif :
#   - avancer étape par étape avec ENTER
#   - vérifier l'environnement Linux
#   - afficher les ressources système
#   - vérifier le réseau
#   - vérifier Sysrepo / Netopeer2
# ============================================================

set -u

pause_step() {
    echo
    read -r -p "Press ENTER to continue..."
    echo
}

section() {
    echo
    echo "============================================================"
    echo " $1"
    echo "============================================================"
}

section "WSL / UBUNTU INSPECTION"
echo "Ce script est en lecture seule."
echo "Il ne modifie ni WSL, ni Ubuntu, ni Sysrepo, ni Netopeer2."
pause_step

section "1. IDENTITE ET SYSTEME"

echo
echo "--- Utilisateur ---"
whoami

echo
echo "--- Repertoire courant ---"
pwd

echo
echo "--- Kernel ---"
uname -a

echo
echo "--- Distribution Linux ---"
cat /etc/os-release

pause_step

section "2. RESSOURCES"

echo
echo "--- Disques ---"
df -h

echo
echo "--- Memoire ---"
free -h

pause_step

section "3. RESEAU"

echo
echo "--- Interfaces ---"
ip addr

echo
echo "--- Routes ---"
ip route

pause_step

section "4. OUTILS SYSREPO / NETCONF"

check_command() {
    local cmd="$1"

    if command -v "$cmd" >/dev/null 2>&1; then
        echo "[OK]      $cmd : $(command -v "$cmd")"
    else
        echo "[ABSENT]  $cmd"
    fi
}

check_command sysrepoctl
check_command sysrepocfg
check_command netopeer2-server

pause_step

section "5. MODULES YANG INSTALLES DANS SYSREPO"

if command -v sysrepoctl >/dev/null 2>&1; then
    sysrepoctl -l
else
    echo "[SKIP] sysrepoctl n'est pas disponible."
fi

pause_step

section "6. PROCESSUS UTILES"

echo
echo "--- Sysrepo / Netopeer2 ---"

ps aux | grep -E 'sysrepo|netopeer2' | grep -v grep || \
    echo "Aucun processus sysrepo/netopeer2 trouve."

pause_step

section "FIN DE L'INSPECTION"
echo "Toutes les étapes ont été exécutées."
echo
