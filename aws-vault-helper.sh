#!/usr/bin/env sh
SHFLAGS=""
case "$SHELL" in
    *zsh*) SHFLAGS="--no-rcs" ;;
    *bash*) SHFLAGS="--norc" ;;
esac
AWS_ENV=$(aws-vault --backend=secret-service exec "$1" -- env | grep AWS)
env ${AWS_ENV} "${PS1} <aws-vault-env ${AWS_VAULT}>" "${SHELL}" "${SHFLAGS}"
