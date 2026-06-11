interface HeaderProps {
  geradoEm: string
}

export function Header({ geradoEm }: HeaderProps) {
  return (
    <header className="bg-[#0E8FA3] text-white px-8 py-5 flex items-center justify-between shadow-md">
      <div>
        <h1 className="text-xl font-bold tracking-wide">Relatório de Fornecedores — Zurich Airport</h1>
        <p className="text-sm opacity-85 mt-1">Conformidade Documental de Terceiros | Plataforma Efcaz</p>
      </div>
      <div className="bg-white/20 border border-white/40 rounded-lg px-4 py-2 text-center text-sm leading-relaxed">
        <span className="block font-bold text-base">{geradoEm}</span>
        <span className="text-xs opacity-80">Use os botões PDF em cada seção para exportar</span>
      </div>
    </header>
  )
}
