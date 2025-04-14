package com.example.demo.dto;

public class CodigoCorrigidoComSimilaridadeDTO {

    private String codigoOriginal;
    private String codigoCorrigido;
    private double similaridade;
    private String origemId; // <-- NOVO

    public CodigoCorrigidoComSimilaridadeDTO(String codigoOriginal, String codigoCorrigido, double similaridade) {
        this.codigoOriginal = codigoOriginal;
        this.codigoCorrigido = codigoCorrigido;
        this.similaridade = similaridade;
    }

    public String getCodigoOriginal() {
        return codigoOriginal;
    }

    public String getCodigoCorrigido() {
        return codigoCorrigido;
    }

    public double getSimilaridade() {
        return similaridade;
    }

    public String getOrigemId() {
        return origemId;
    }

    public void setOrigemId(String origemId) {
        this.origemId = origemId;
    }
}
