package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;

public class ApontamentoDTO {

    private String codigo;
    private String tipo;

    @JsonIgnore
    private String linguagem;
    @JsonIgnore
    private String contexto;

    private String exemplo;
    private String correcao;

    public String getExemplo() {
        return exemplo;
    }

    public void setExemplo(String exemplo) {
        this.exemplo = exemplo;
    }

    public String getCorrecao() {
        return correcao;
    }

    public void setCorrecao(String correcao) {
        this.correcao = correcao;
    }

    public String getCodigo() {
        return codigo;
    }

    public void setCodigo(String codigo) {
        this.codigo = codigo;
    }

    public String getTipo() {
        return tipo;
    }

    public void setTipo(String tipo) {
        this.tipo = tipo;
    }

    public String getLinguagem() {
        return linguagem;
    }

    public void setLinguagem(String linguagem) {
        this.linguagem = linguagem;
    }

    public String getContexto() {
        return contexto;
    }

    public void setContexto(String contexto) {
        this.contexto = contexto;
    }
}
