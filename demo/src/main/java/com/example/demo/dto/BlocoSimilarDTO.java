package com.example.demo.dto;

public class BlocoSimilarDTO {

    private String blocoOriginal;
    private String blocoCorrigido;
    private String nomeMetodo;
    private double similaridade;
    private String origemId;

    public String getBlocoOriginal() {
        return blocoOriginal;
    }

    public void setBlocoOriginal(String blocoOriginal) {
        this.blocoOriginal = blocoOriginal;
    }

    public String getBlocoCorrigido() {
        return blocoCorrigido;
    }

    public void setBlocoCorrigido(String blocoCorrigido) {
        this.blocoCorrigido = blocoCorrigido;
    }

    public String getNomeMetodo() {
        return nomeMetodo;
    }

    public void setNomeMetodo(String nomeMetodo) {
        this.nomeMetodo = nomeMetodo;
    }

    public double getSimilaridade() {
        return similaridade;
    }

    public void setSimilaridade(double similaridade) {
        this.similaridade = similaridade;
    }

    public String getOrigemId() {
        return origemId;
    }

    public void setOrigemId(String origemId) {
        this.origemId = origemId;
    }
}
