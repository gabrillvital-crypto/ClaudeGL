export function AuditAlert() {
  return (
    <div className="rounded-xl overflow-hidden shadow-md mb-5 border-2 border-[#DC3545]" style={{ background: '#fff0f0' }}>
      <div className="bg-[#DC3545] text-white px-5 py-3.5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="font-bold text-[16px]">NEPOS SISTEMAS DE CONTROLE E AUTOMACAO LTDA</div>
          <div className="text-[12px] opacity-85">Aeroporto: VIX (Vitória) &nbsp;|&nbsp; Competência: Março/2026 &nbsp;|&nbsp; Relatório: 20/05/2026</div>
        </div>
        <span className="bg-white text-[#DC3545] font-black px-4 py-1 rounded-full text-[13px] tracking-wide">REPROVADO</span>
      </div>
      <div className="p-5">
        <div className="bg-[#ffeaea] border-l-4 border-[#DC3545] rounded-r px-4 py-3 text-[13px] text-[#555] mb-4 leading-relaxed">
          <strong>Parecer Técnico:</strong> A auditoria mapeou um cenário de colapso nos prazos de compliance financeiro e fiscal com atrasos acumulados desde o início de 2026 (CRF FGTS, DCTFWEB, GFD, FOPAG e Comprovantes Salariais vencidos entre janeiro e fevereiro). Na área ocupacional (SST), há bloqueio sistêmico crítico pela ausência total do PGR e rejeição técnica do PCMSO, paralisando a validação de todos os terceiros ativos. O ex-colaborador Fabio Almeida Tozi apresenta vício gravíssimo de ponto britânico e omissão do Kit Rescisão. <strong>Exposição máxima da contratante a passivos trabalhistas, fiscais e previdenciários.</strong>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-[13px] font-bold text-[#DC3545] uppercase tracking-wide mb-2">Documentação da Empresa</div>
            <table className="w-full text-[12.5px] border-collapse">
              <thead>
                <tr className="border-b-2 border-[#ddd]">
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Documento</th>
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Vencimento</th>
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Situação</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Certificado de Regularidade FGTS (CRF)', '25/02/2026', 'VENCIDO', 'red'],
                  ['DCTFWEB', '20/02/2026', 'VENCIDO', 'red'],
                  ['FOPAG (Folha de Pagamento)', '30/01/2026', 'VENCIDO', 'red'],
                  ['GFD (FGTS Digital Mensal)', '09/02/2026', 'VENCIDO', 'red'],
                  ['Comprovante Bancário de Salários', '05/02/2026', 'VENCIDO', 'red'],
                  ['Certidões TRF3 (Criminal e Civil)', '23/03/2026', 'VENCIDO', 'red'],
                  ['PGR (Programa Base)', 'Não enviado', 'PENDENTE', 'yellow'],
                  ['CIPA (Composição NR-05)', 'Não enviado', 'PENDENTE', 'yellow'],
                  ['PCMSO (Programa Base)', 'Inadequado', 'ANEXO INCORRETO', 'orange'],
                  ['Laudos de Insalubridade/Periculosidade', 'Não enviado', 'PENDENTE', 'yellow'],
                  ['SESMT (Composição NR-04)', 'Não enviado', 'PENDENTE', 'yellow'],
                ].map(([doc, venc, sit, cor], i) => (
                  <tr key={i} className="border-b border-[#eee] hover:bg-[#fff5f5]">
                    <td className="py-1.5 px-2">{doc}</td>
                    <td className="py-1.5 px-2">{venc}</td>
                    <td className={`py-1.5 px-2 font-bold ${cor === 'red' ? 'text-[#DC3545]' : cor === 'yellow' ? 'text-[#a07800]' : 'text-[#F4793B]'}`}>{sit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <div className="text-[13px] font-bold text-[#DC3545] uppercase tracking-wide mb-2">Prontuários de Trabalhadores</div>
            <table className="w-full text-[12.5px] border-collapse">
              <thead>
                <tr className="border-b-2 border-[#ddd]">
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Colaborador</th>
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Vínculo</th>
                  <th className="text-left py-2 px-2 text-[#555] font-bold">Situação</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-[#eee] hover:bg-[#fff5f5]">
                  <td className="py-1.5 px-2"><strong>Claudio Marinho Coutinho</strong><br /><small className="text-[11px] text-[#666]">Ponto vencido 27/04/2026. Ficha EPI não anexada. ASO/OS bloqueados por falta de PGR/PCMSO.</small></td>
                  <td className="py-1.5 px-2">Efetivo Ativo</td>
                  <td className="py-1.5 px-2 font-bold text-[#DC3545]">REPROVADO / BLOQUEADO</td>
                </tr>
                <tr className="border-b border-[#eee] hover:bg-[#fff5f5]">
                  <td className="py-1.5 px-2"><strong>Fabio Almeida Tozi</strong><br /><small className="text-[11px] text-[#666]">Omissão total do Kit Rescisão e Ficha EPI. Ponto britânico (marcação invariável).</small></td>
                  <td className="py-1.5 px-2">Inativo — Desligado 16/03/2026</td>
                  <td className="py-1.5 px-2 font-bold text-[#DC3545]">REPROVADO (RESCISÃO)</td>
                </tr>
                <tr className="border-b border-[#eee] hover:bg-[#fff5f5]">
                  <td className="py-1.5 px-2"><strong>Demais colaboradores ativos</strong><br /><small className="text-[11px] text-[#666]">Bloqueio cascata: ASO, EPI e OS suspensos pela ausência do PGR e inadequação do PCMSO.</small></td>
                  <td className="py-1.5 px-2">Efetivos Ativos</td>
                  <td className="py-1.5 px-2 font-bold text-[#6f42c1]">BLOQUEADO</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
