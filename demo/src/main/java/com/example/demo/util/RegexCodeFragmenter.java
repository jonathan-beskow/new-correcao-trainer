package com.example.demo.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.*;

public class RegexCodeFragmenter {

    private static final Logger log = LoggerFactory.getLogger(RegexCodeFragmenter.class);

    /**
     * Extrai blocos de código com base no tipo de linguagem especificado.
     *
     * @param codigo O código completo a ser analisado
     * @param tipo   A linguagem ou categoria (js, html, jsp, jsp_misto...)
     * @return Lista de blocos encontrados
     */
    public static List<String> extrairBlocos(String codigo, String tipo) {
        List<String> blocos = new ArrayList<>();

        if (codigo == null || tipo == null) {
            log.warn("⚠️ Código ou tipo nulo recebido. Ignorando extração.");
            return blocos;
        }

        String tipoNormalizado = tipo.trim().toLowerCase();
        String regex = obterRegexPorTipo(tipoNormalizado);

        if (regex.isEmpty()) {
            log.warn("⚠️ Nenhum regex definido para linguagem '{}'. Fragmentação ignorada.", tipo);
            return blocos;
        }

        try {
            Pattern pattern = Pattern.compile(regex, Pattern.CASE_INSENSITIVE | Pattern.MULTILINE | Pattern.DOTALL);
            Matcher matcher = pattern.matcher(codigo);

            int count = 0;
            while (matcher.find()) {
                String bloco = matcher.group().trim();
                blocos.add(bloco);
                count++;
            }

            log.info("✅ Extraídos {} blocos para linguagem '{}'.", count, tipo);
        } catch (PatternSyntaxException e) {
            log.error("❌ Erro no regex para tipo '{}': {}", tipo, e.getMessage());
        } catch (Exception e) {
            log.error("❌ Erro inesperado durante extração de blocos para '{}': {}", tipo, e.getMessage());
        }

        return blocos;
    }

    /**
     * Define o regex apropriado para cada tipo de código.
     */
    private static String obterRegexPorTipo(String tipo) {
        switch (tipo) {
            case "js":
                return "function\\s+[a-zA-Z_$][a-zA-Z\\d_$]*\\s*\\([^)]*\\)\\s*\\{(?:[^{}]*|\\{[^{}]*\\})*\\}";
            case "html":
                return "<(div|form|script|section|article)[^>]*>[\\s\\S]*?</\\1>";
            case "jsp":
                return "<%[\\s\\S]*?%>|<jsp:[a-zA-Z]+[^>]*>[\\s\\S]*?</jsp:[a-zA-Z]+>|<form:[a-zA-Z]+[^>]*>[\\s\\S]*?</form:[a-zA-Z]+>";
            case "jstl":
                return "<c:[a-zA-Z]+[^>]*>[\\s\\S]*?</c:[a-zA-Z]+>";
            case "jsp_misto":
                return String.join("|",
                        "<%[\\s\\S]*?%>",
                        "<jsp:attribute[^>]*>[\\s\\S]*?</jsp:attribute>",
                        "<jsp:[a-zA-Z]+[^>]*>[\\s\\S]*?</jsp:[a-zA-Z]+>",
                        "<form:form[^>]*>",
                        "</form:form>",
                        "<form:[a-zA-Z]+[^>]*>[\\s\\S]*?</form:[a-zA-Z]+>",
                        "<form:[a-zA-Z]+[^>]*?/?>",
                        "<input[^>]+type=\\s*[\"']hidden[\"'][^>]*csrfToken[^>]*?>",
                        "<c:[a-zA-Z]+[^>]*>[\\s\\S]*?</c:[a-zA-Z]+>",
                        "<(div|section|article)[^>]*>[\\s\\S]*?</\\1>",
                        "<script[^>]*>[\\s\\S]*?</script>"
                );
            default:
                return "";
        }
    }

    /**
     * Remove espaços, comentários e scripts do bloco para comparação lógica.
     */
    public static String normalizarBloco(String bloco) {
        return bloco
                .replaceAll("<!--.*?-->", "")
                .replaceAll("(?s)<script[^>]*?>.*?</script>", "")
                .replaceAll("\\s+", "")
                .trim();
    }
}
