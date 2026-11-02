// Conexión con SUNAT SIMULADA. Este curso es solo frontend: no se llama a ningún servicio real.
// El resto de la app solo usa estas funciones; para conectar una API real bastaría cambiar este archivo.

const Sunat = (() => {
  const PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
  const LIMITE_BOLETA_SIN_DNI = 700; // desde este monto la boleta pide identificar al cliente
  const IGV = 0.18;

  // Dígito verificador del RUC (módulo 11), el mismo que valida SUNAT.
  function digitoRUC(base10) {
    const suma = [...base10].reduce((acc, d, i) => acc + Number(d) * PESOS[i], 0);
    const r = 11 - (suma % 11);
    return r === 10 ? 0 : r === 11 ? 1 : r;
  }
  const rucValido = r => /^(10|15|17|20)\d{9}$/.test(r) && digitoRUC(r.slice(0, 10)) === Number(r[10]);
  const dniValido = d => /^\d{8}$/.test(d);

  const conDigito = base => base + digitoRUC(base);
  // Contribuyentes ficticios con RUC de formato válido, solo para probar la pantalla.
  const PADRON_RUC = {
    [conDigito('2060000001')]: { nombre: 'DISTRIBUIDORA EJEMPLO S.A.C.', estado: 'ACTIVO', condicion: 'HABIDO' },
    [conDigito('2060000002')]: { nombre: 'ABARROTES LA ESQUINA E.I.R.L.', estado: 'ACTIVO', condicion: 'HABIDO' },
    [conDigito('1070000003')]: { nombre: 'PERSONA DE EJEMPLO UNO', estado: 'ACTIVO', condicion: 'HABIDO' }
  };
  const PADRON_DNI = { '12345678': 'CLIENTE DE EJEMPLO UNO', '87654321': 'CLIENTE DE EJEMPLO DOS' };
  const ejemplos = { rucs: Object.keys(PADRON_RUC), dni: Object.keys(PADRON_DNI) };

  function consultar(numero) {
    return new Promise((ok, mal) => {
      if (!Red.enLinea()) return mal(new Error('sin-red'));
      setTimeout(() => {
        const r = numero.length === 11 ? PADRON_RUC[numero] : PADRON_DNI[numero] && { nombre: PADRON_DNI[numero] };
        return r ? ok({ numero, ...r }) : mal(new Error('no-encontrado'));
      }, 600);
    });
  }

  function emitir({ tipo, total, cliente, fecha }) {
    const serie = tipo === 'factura' ? 'F001' : 'B001';
    const numero = Datos.siguienteCorrelativo(serie);
    const base = Datos.redondear(total / (1 + IGV));
    return {
      tipo, serie, numero, codigo: `${serie}-${String(numero).padStart(8, '0')}`, fecha, cliente,
      base, igv: Datos.redondear(total - base), total,
      estado: Red.enLinea() ? 'aceptado' : 'pendiente'
    };
  }

  // Al volver internet, los comprobantes guardados sin conexión pasan a "aceptado".
  function enviarPendientes() {
    let enviados = 0;
    Datos.ventas().forEach(v => {
      if (v.comprobante && v.comprobante.estado === 'pendiente') { v.comprobante.estado = 'aceptado'; enviados++; }
    });
    if (enviados) Datos.persistir();
    return enviados;
  }

  const etiquetaEstado = e => e === 'aceptado' ? 'Aceptado por SUNAT (simulado)' : 'Pendiente de envío';

  return { rucValido, dniValido, consultar, emitir, enviarPendientes, etiquetaEstado, ejemplos, LIMITE_BOLETA_SIN_DNI };
})();
