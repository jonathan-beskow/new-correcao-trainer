package com.example.demo.service;

import com.example.demo.dto.ApontamentoDTO;
import com.example.demo.dto.BlocoSimilarDTO;
import com.example.demo.dto.CodigoCorrigidoComSimilaridadeDTO;
import com.example.demo.dto.SugestaoCorrecaoDTO;
import com.example.demo.util.LinguagemDetector;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
public class CorrecaoOrquestradorService {

    @Autowired private SimilaridadeService similaridadeService;
    @Autowired
    private CodeCorrectionService codeCorrectionService;

    public SugestaoCorrecaoDTO processarCorrecao(ApontamentoDTO dto, boolean usarFallbackForcado) {
        String linguagem = LinguagemDetector.detectarLinguagem(dto.getCodigo());
        if ("html".equals(linguagem) && dto.getCodigo().contains("<%@")) {
            linguagem = "jsp_misto";
        }

        List<CodigoCorrigidoComSimilaridadeDTO> similares = similaridadeService.buscarSimilaresTopK(dto.getCodigo(), dto.getTipo(), 3);
        if (similares.isEmpty()) {
            return new SugestaoCorrecaoDTO(dto.getTipo(), linguagem, dto.getContexto(), dto.getCodigo(),
                    "Nenhuma sugestão encontrada", "Não foram encontrados casos semelhantes.", 0.0);
        }

        CodigoCorrigidoComSimilaridadeDTO caso = similares.getFirst();
        BlocoSimilarDTO bloco = similaridadeService.getBlocoMaisSimilar();

        String origemId = (bloco != null && bloco.getOrigemId() != null) ? bloco.getOrigemId() : caso.getOrigemId();

        String resposta = usarFallbackForcado
                ? codeCorrectionService.gerarCorrecaoViaChatGPT(dto.getTipo(), caso.getCodigoOriginal(), caso.getCodigoCorrigido(), dto.getCodigo())
                : codeCorrectionService.sugerirComFallback(dto.getTipo(), caso.getCodigoOriginal(), caso.getCodigoCorrigido(), dto.getCodigo(), origemId, bloco);

        double similaridade = new BigDecimal(caso.getSimilaridade()).setScale(4, RoundingMode.HALF_UP).doubleValue();

        return new SugestaoCorrecaoDTO(dto.getTipo(), linguagem, dto.getCodigo(), resposta,
                usarFallbackForcado ? "Correção via fallback GPT" : "Correção baseada em similaridade",
                similaridade);
    }
}

