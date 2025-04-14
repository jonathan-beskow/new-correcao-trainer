package com.example.demo.model;

public class BlocoCorrigido {
    private String nomeMetodo;
    private String tipo;
    private String blocoAntes;
    private String blocoDepois;
    private String origemId;

    public BlocoCorrigido(String nomeMetodo, String tipo, String blocoAntes, String blocoDepois, String origemId) {
        this.nomeMetodo = nomeMetodo;
        this.tipo = tipo;
        this.blocoAntes = blocoAntes;
        this.blocoDepois = blocoDepois;
        this.origemId = origemId;
    }

    public String getNomeMetodo() {
        return nomeMetodo;
    }

    public String getTipo() {
        return tipo;
    }

    public String getBlocoAntes() {
        return blocoAntes;
    }

    public String getBlocoDepois() {
        return blocoDepois;
    }

    public String getOrigemId() {
        return origemId;
    }
}