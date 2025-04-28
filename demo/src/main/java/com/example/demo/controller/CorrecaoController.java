package com.example.demo.controller;

import com.example.demo.dto.ApontamentoDTO;
import com.example.demo.dto.SugestaoCorrecaoDTO;
import com.example.demo.model.CasoCorrigido;
import com.example.demo.service.CorrecaoOrquestradorService;
import com.example.demo.service.saveService.InserirCasoCorrigidoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;


@RestController
@RequestMapping("/sugerir-correcao")
public class CorrecaoController {

    @Autowired
    private CorrecaoOrquestradorService correcaoOrquestrador;
    @Autowired
    private InserirCasoCorrigidoService inserirCasoService;

    @PostMapping("/corrigir")
    public ResponseEntity<SugestaoCorrecaoDTO> corrigir(@RequestBody ApontamentoDTO dto) {
        SugestaoCorrecaoDTO resposta = correcaoOrquestrador.processarCorrecao(dto, false);
        return ResponseEntity.ok(resposta);
    }

    @PostMapping("/fallback")
    public ResponseEntity<SugestaoCorrecaoDTO> corrigirComFallback(@RequestBody ApontamentoDTO dto) {
        SugestaoCorrecaoDTO resposta = correcaoOrquestrador.processarCorrecao(dto, true);
        return ResponseEntity.ok(resposta);
    }

    @PostMapping("/cadastrar-caso")
    public ResponseEntity<Map<String, String>> cadastrar(@RequestBody CasoCorrigido caso) {
        return inserirCasoService.inserir(caso);
    }
}
