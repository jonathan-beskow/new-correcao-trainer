package com.example.demo.util;


public class LinguagemDetector {

    public static String detectarLinguagem(String codigo) {
        String code = codigo.toLowerCase();

        if (code.contains("public class") || code.contains("import java") || code.contains("@Override")) {
            return "java";
        } else if (code.contains("<html") || code.contains("<div") || code.contains("</body>")) {
            return "html";
        } else if (code.contains("<%") || code.contains("pageContext") || code.contains("request.getParameter")) {
            return "jsp";
        } else if (code.contains("<c:if") || code.contains("c:choose") || code.contains("<c:forEach")) {
            return "jstl";
        } else if (code.contains("function") && code.contains("{") && code.contains("}") && code.contains("()")) {
            return "js";
        } else if (code.contains("select ") || code.contains("from ") || code.contains("where ")) {
            return "sql";
        }

        return "desconhecida";
    }
}

