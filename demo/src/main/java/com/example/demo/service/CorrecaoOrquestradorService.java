package com.example.demo.service;

import com.example.demo.dto.ApontamentoDTO;
import com.example.demo.dto.BlocoSimilarDTO;
import com.example.demo.dto.CodigoCorrigidoComSimilaridadeDTO;
import com.example.demo.dto.SugestaoCorrecaoDTO;
import com.example.demo.util.LinguagemDetector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
public class CorrecaoOrquestradorService {

    private static final Logger logger = LoggerFactory.getLogger(CorrecaoOrquestradorService.class);

    @Autowired
    private SimilaridadeService similaridadeService;
    @Autowired
    private CodeCorrectionService codeCorrectionService;

//    public SugestaoCorrecaoDTO processarCorrecao(ApontamentoDTO dto, boolean usarFallbackForcado) {
//        String linguagem = LinguagemDetector.detectarLinguagem(dto.getCodigo());
//        if ("html".equals(linguagem) && dto.getCodigo().contains("<%@")) {
//            linguagem = "jsp_misto";
//        }
//
//        List<CodigoCorrigidoComSimilaridadeDTO> similares = similaridadeService.buscarSimilaresTopK(dto.getCodigo(), dto.getTipo(), 3);
//        CodigoCorrigidoComSimilaridadeDTO caso = !similares.isEmpty() ? similares.getFirst() : null;
//        BlocoSimilarDTO bloco = similaridadeService.getBlocoMaisSimilar();
//
//        String origemId = (bloco != null && bloco.getOrigemId() != null) ? bloco.getOrigemId() :
//                (caso != null ? caso.getOrigemId() : null);
//
//        String resposta;
//        boolean fallbackAtivado = usarFallbackForcado || caso == null;
//
//        if (fallbackAtivado) {
//            logger.warn("⚠️ Nenhum similar encontrado ou fallback forçado. Chamando GPT...");
//            resposta = codeCorrectionService.gerarCorrecaoViaChatGPT(
//                    dto.getTipo(), dto.getCodigo(), dto.getContexto(), dto.getCodigo()
//            );
//        } else {
//            resposta = codeCorrectionService.sugerirComFallback(
//                    dto.getTipo(), caso.getCodigoOriginal(), caso.getCodigoCorrigido(), dto.getCodigo(), origemId, bloco
//            );
//        }
//
//        // Se resposta do fallback for vazia ou erro, garantir uma resposta padrão
//        if (resposta == null || resposta.isBlank() || resposta.toLowerCase().contains("erro")) {
//            resposta = "Nenhuma sugestão encontrada.";
//            logger.error("❌ Falha ao gerar correção, resposta final: Nenhuma sugestão encontrada.");
//        }
//
//        double similaridade = (caso != null)
//                ? new BigDecimal(caso.getSimilaridade()).setScale(4, RoundingMode.HALF_UP).doubleValue()
//                : 0.0;
//
//        return new SugestaoCorrecaoDTO(
//                dto.getTipo(),
//                linguagem,
//                dto.getCodigo(),
//                resposta,
//                (fallbackAtivado ? "Correção via fallback GPT" : "Correção baseada em similaridade"),
//                similaridade
//        );
//    }

    public SugestaoCorrecaoDTO processarCorrecao(ApontamentoDTO dto, boolean usarFallbackForcado) {
        String linguagem = LinguagemDetector.detectarLinguagem(dto.getCodigo());
        if ("html".equals(linguagem) && dto.getCodigo().contains("<%@")) {
            linguagem = "jsp_misto";
        }

        List<CodigoCorrigidoComSimilaridadeDTO> similares = similaridadeService.buscarSimilaresTopK(dto.getCodigo(), dto.getTipo(), 3);
        CodigoCorrigidoComSimilaridadeDTO caso = !similares.isEmpty() ? similares.getFirst() : null;
        BlocoSimilarDTO bloco = similaridadeService.getBlocoMaisSimilar();

        String origemId = (bloco != null && bloco.getOrigemId() != null) ? bloco.getOrigemId() :
                (caso != null ? caso.getOrigemId() : null);

        String resposta;
        boolean fallbackAtivado = usarFallbackForcado || caso == null;

        if (fallbackAtivado) {
            logger.warn("⚠️ Nenhum similar encontrado ou fallback forçado. Chamando GPT...");
            resposta = codeCorrectionService.gerarCorrecaoViaChatGPT(
                    dto.getTipo(), dto.getCodigo(), dto.getContexto(), dto.getCodigo()
            );
        } else {
            resposta = codeCorrectionService.sugerirComFallback(
                    dto.getTipo(), caso.getCodigoOriginal(), caso.getCodigoCorrigido(), dto.getCodigo(), origemId, bloco
            );
        }

        // Melhor validação para detectar erro de verdade na resposta
        if (resposta == null
                || resposta.isBlank()
                || resposta.trim().equalsIgnoreCase("Erro ao usar ChatGPT.")
                || resposta.trim().equalsIgnoreCase("Erro: resposta vazia do modelo ChatGPT.")) {
            resposta = "Nenhuma sugestão encontrada.";
            logger.error("❌ Falha ao gerar correção, resposta final: Nenhuma sugestão encontrada.");
        }

        double similaridade = (caso != null)
                ? new BigDecimal(caso.getSimilaridade()).setScale(4, RoundingMode.HALF_UP).doubleValue()
                : 0.0;

        return new SugestaoCorrecaoDTO(
                dto.getTipo(),
                linguagem,
                dto.getCodigo(),
                resposta,
                (fallbackAtivado ? "Correção via fallback GPT" : "Correção baseada em similaridade"),
                similaridade
        );
    }

}
