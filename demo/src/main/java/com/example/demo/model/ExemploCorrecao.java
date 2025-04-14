package com.example.demo.model;

public class ExemploCorrecao {
    private String blocoAntes;
    private String blocoDepois;
    private int numeroBloco;

    public ExemploCorrecao(String blocoAntes, String blocoDepois, int numeroBloco) {
        this.blocoAntes = blocoAntes;
        this.blocoDepois = blocoDepois;
        this.numeroBloco = numeroBloco;
    }

    public String getBlocoAntes() { return blocoAntes; }
    public String getBlocoDepois() { return blocoDepois; }
    public int getNumeroBloco() { return numeroBloco; }
}
