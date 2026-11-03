#!/usr/bin/env bash

# ============================================================
# WSL / Ubuntu inspection script
# Objectif :
#   - vérifier l'environnement Linux
#   - afficher les ressources système
#   - vérifier le réseau
#   - vérifier Sysrepo / Netopeer2
# ============================================================

set -u

echo
echo "============================================================"
echo " 1. IDENTITE ET SYSTEME"
echo "============================================================"

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


echo
echo "============================================================"
echo " 2. RESSOURCES"
echo "============================================================"

echo
echo "--- Disques ---"
df -h

echo
echo "--- Memoire ---"
free -h


echo
echo "============================================================"
echo " 3. RESEAU"
echo "============================================================"

echo
echo "--- Interfaces ---"
ip addr

echo
echo "--- Routes ---"
ip route


echo
echo "============================================================"
echo " 4. OUTILS SYSREPO / NETCONF"
echo "============================================================"

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


echo
echo "============================================================"
echo " 5. MODULES YANG INSTALLES DANS SYSREPO"
echo "============================================================"

if command -v sysrepoctl >/dev/null 2>&1; then
    sysrepoctl -l
else
    echo "[SKIP] sysrepoctl n'est pas disponible."
fi


echo
echo "============================================================"
echo " 6. PROCESSUS UTILES"
echo "============================================================"

echo
echo "--- Sysrepo / Netopeer2 ---"

ps aux | grep -E 'sysrepo|netopeer2' | grep -v grep || \
    echo "Aucun processus sysrepo/netopeer2 trouve."


echo
echo "============================================================"
echo " FIN DE L'INSPECTION"
echo "============================================================"
echo
