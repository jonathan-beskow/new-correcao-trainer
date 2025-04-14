package com.example.demo.model;

public class CasoCorrigidoComSimilaridade {
    private final CasoCorrigido caso;
    private final double similaridade;

    public CasoCorrigidoComSimilaridade(CasoCorrigido caso, double similaridade) {
        this.caso = caso;
        this.similaridade = similaridade;
    }

    public CasoCorrigido getCaso() {
        return caso;
    }

    public double getSimilaridade() {
        return similaridade;
    }
}