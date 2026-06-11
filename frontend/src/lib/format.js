// Formatea un número como monto (1,250.00), estilo Guatemala.
export const money = (n) =>
  Number(n || 0).toLocaleString('es-GT', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

// Fecha de hoy en formato YYYY-MM-DD (para inputs date).
export const hoy = () => new Date().toISOString().slice(0, 10)
