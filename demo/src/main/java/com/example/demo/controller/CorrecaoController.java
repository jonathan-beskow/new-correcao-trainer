package com.example.demo.controller;

import com.example.demo.dto.ApontamentoDTO;
import com.example.demo.dto.BlocoSimilarDTO;
import com.example.demo.dto.CodigoCorrigidoComSimilaridadeDTO;
import com.example.demo.dto.SugestaoCorrecaoDTO;
import com.example.demo.model.CasoCorrigido;
import com.example.demo.service.CodeCorrectionService;
import com.example.demo.service.SimilaridadeService;
import com.example.demo.service.saveService.InserirCasoCorrigidoService;
import com.example.demo.util.LinguagemDetector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


@RestController
@RequestMapping("/sugerir-correcao")
public class CorrecaoController {

    private static final Logger logger = LoggerFactory.getLogger(CorrecaoController.class);

    @Autowired
    private CodeCorrectionService codeCorrectionService;

    @Autowired
    private SimilaridadeService similaridadeService;

    @Autowired
    private InserirCasoCorrigidoService inserirCasoCorrigidoService;


    @PostMapping("/corrigir")
    public SugestaoCorrecaoDTO corrigir(@RequestBody ApontamentoDTO dto) {
        String linguagemDetectada = LinguagemDetector.detectarLinguagem(dto.getCodigo());
        if ("html".equals(linguagemDetectada) && dto.getCodigo().contains("<%@")) {
            linguagemDetectada = "jsp_misto";
        }

        List<CodigoCorrigidoComSimilaridadeDTO> similares =
                similaridadeService.buscarSimilaresTopK(dto.getCodigo(), dto.getTipo(), 3);

        if (similares.isEmpty()) {
            return new SugestaoCorrecaoDTO(dto.getTipo(), linguagemDetectada, dto.getContexto(), dto.getCodigo(),
                    "Nenhuma sugestão encontrada", "Não foram encontrados casos semelhantes no banco de dados.", 0.0);
        }

        CodigoCorrigidoComSimilaridadeDTO resultado = similares.getFirst();
        BlocoSimilarDTO bloco = similaridadeService.getBlocoMaisSimilar();

        String origemIdParaCorrecao = (bloco != null && bloco.getOrigemId() != null)
                ? bloco.getOrigemId()
                : resultado.getOrigemId(); // fallback para a classe, se o bloco não tiver origem

        if (bloco != null) {
            logger.info("🔍 Bloco mais similar encontrado:");
            logger.info("🔢 Similaridade (bloco): {}", bloco.getSimilaridade());
            logger.info("🟥 Bloco vulnerável:\n{}", bloco.getBlocoOriginal());
            logger.info("🟩 Bloco corrigido:\n{}", bloco.getBlocoCorrigido());
            logger.info("🆔 Origem ID do bloco: {}", origemIdParaCorrecao);
        } else {
            logger.info("⚠️ Nenhum bloco similar encontrado. Usando origem da classe.");
            logger.info("🆔 Origem ID da classe: {}", origemIdParaCorrecao);
        }

        // Sugestão com fallback para GPT se necessário
        String classeFinalCorrigida = codeCorrectionService.sugerirComFallback(
                dto.getTipo(),
                resultado.getCodigoOriginal(),
                resultado.getCodigoCorrigido(),
                dto.getCodigo(),
                origemIdParaCorrecao,
                bloco // ainda é útil passar os blocos mesmo se for para o fallback
        );

        double similaridadeFormatada = new BigDecimal(resultado.getSimilaridade())
                .setScale(4, RoundingMode.HALF_UP)
                .doubleValue();

        return new SugestaoCorrecaoDTO(
                dto.getTipo(),
                linguagemDetectada,
                dto.getCodigo(),
                classeFinalCorrigida,
                "Correção gerada com base em exemplo similar",
                similaridadeFormatada
        );
    }



    @PostMapping("/cadastrar-caso")
    public ResponseEntity<Map<String, String>> cadastrarCaso(@RequestBody CasoCorrigido novoCaso) {
        Map<String, String> resposta = new HashMap<>();

        if (novoCaso.getTipo() == null || novoCaso.getTipo().trim().isEmpty()) {
            resposta.put("mensagem", "O campo 'tipo' é obrigatório.");
            return ResponseEntity.badRequest().body(resposta);
        }

        String tipoNormalizado = novoCaso.getTipo().trim();
        tipoNormalizado = tipoNormalizado.substring(0, 1).toUpperCase() + tipoNormalizado.substring(1).toLowerCase();
        novoCaso.setTipo(tipoNormalizado);

        boolean sucesso = inserirCasoCorrigidoService.inserirCasoCorrigido(novoCaso);

        if (sucesso) {
            logger.info("Novo caso corrigido cadastrado com sucesso:\n{}", novoCaso.getCodigoCorrigido());
            resposta.put("mensagem", "Caso inserido com sucesso.");
            return ResponseEntity.ok(resposta);
        } else {
            logger.error("Erro ao tentar cadastrar o caso.");
            resposta.put("mensagem", "Erro ao inserir caso.");
            return ResponseEntity.status(500).body(resposta);
        }
    }
}
