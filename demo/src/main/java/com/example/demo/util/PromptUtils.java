package com.example.demo.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PromptUtils {

    private static final Logger logger = LoggerFactory.getLogger(PromptUtils.class);

    public static String generatePrompt(String tipo, String codigoOriginal, String codigoCorrigido, String codigoAlvo) {
        return String.format("""
        Corrija o seguinte código vulnerável aplicando uma abordagem semelhante à usada no exemplo anterior.

        Tipo de vulnerabilidade: %s

        Exemplo de código vulnerável:
        %s

        Correção aplicada:
        %s

        Código a ser corrigido:
        %s

        Código corrigido (retorne apenas o novo código, sem comentários ou explicações):
        """, tipo, codigoOriginal, codigoCorrigido, codigoAlvo);
    }


    public static String generatePrompt(String tipo, String codigoCorrigido, String codigoAlvo) {
        return String.format("""
        Observe este exemplo de correção:
        %s
        
        aplique a mesma estrategia de correção de apontamentos do tipo %s no codigo a seguir
        Código a ser corrigido:
        %s
        (retorne apenas o novo código)
        """, codigoCorrigido,tipo, codigoAlvo);
    }


    public static String generatePromptWithOutBase(String tipo, String codigoAlvo) {
        return String.format("""
        O código abaixo apresenta uma vulnerabilidade do tipo %s.
        Corrija-o da forma menos invasiva possível, mantendo a lógica e estrutura original.
        Código a ser corrigido:
        %s
        (retorne apenas o novo código)
        """, tipo, codigoAlvo);
    }

}
