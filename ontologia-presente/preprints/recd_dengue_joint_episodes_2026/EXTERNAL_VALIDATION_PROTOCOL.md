# PROTOCOLO DE VALIDACIÓN EXTERNA — SISTEMA RECD + ONTOLOGÍA DEL PRESENTE

## 1. Objetivo general
Validar y calibrar el sistema de alerta temprana basado en episodios Joint (co-ocurrencia de Capa 1 + Capa 2) como predictor de Capa 3 (reorganización estructural) en contextos operativos reales de vigilancia de dengue en Puerto Rico.

## 2. Principios ontológicos que guían la validación
- Un episodio Joint es una **unidad ontológica** (no un punto aislado).
- La validación debe respetar la temporalidad causal: la señal C1+C2 debe preceder a C3.
- El Confidence Score debe ser interpretable como grado de evidencia de que una configuración C1+C2 está madurando hacia reorganización.

## 3. Estrategias de adquisición de datos externos (Puerto Rico)

### 3.1 Datos históricos extendidos
- Solicitar series completas DengAI o equivalentes para San Juan e Iquitos desde 2000-2005 hasta la fecha actual (o al menos 2010-2025).
- Obtener variables climáticas, demográficas y de intervención (fumigaciones, etc.) para controlar confusores.

### 3.2 Otras ciudades y regiones de Puerto Rico
- Mayagüez, Ponce, Caguas, Bayamón y municipios del interior.
- Diferentes perfiles de transmisión (urbano denso vs peri-urbano vs rural).
- Esto permite testear generalización del Confidence Score más allá de los dos sitios originales.

### 3.3 Colaboración con vigilancia epidemiológica
- Acuerdo con el Departamento de Salud de Puerto Rico o CDC Dengue Branch.
- Definir "ground truth operativo": ¿en qué fecha real se activó respuesta, se declaró brote, se reforzó control vectorial?
- Esto es más valioso que solo picos de incidencia.

### 3.4 Diferenciación San Juan vs Iquitos
**San Juan (recomendado para piloto inicial):**
- Mayor número histórico de episodios Joint observados.
- Mayor densidad de datos → permite calibración estable del Confidence Score.
- Walk-forward multi-año viable.

**Iquitos (caso de baja prevalencia de C2):**
- Muy pocos episodios Joint → la señal de permeabilidad sostenida es rara.
- Estrategia: umbrales adaptativos más bajos + énfasis en duración y consistencia C1.
- Posiblemente requiera features adicionales (ej. humedad sostenida, vegetación) para detectar C2.

## 4. Diseño de validación propuesto

### 4.1 Walk-forward temporal extendido
- Usar primeros 60-70% de la serie para "entrenamiento de pesos y thresholds".
- Evaluar en bloques futuros de 1-2 años, repitiendo de forma rolling.
- Métricas principales: utilidad operativa, lead-time efectivo, tasa de falsas alarmas por categoría, cobertura de brotes reales.

### 4.2 Validación con datos sintéticos (Fase 8)
- Generar 3-5 regímenes (San Juan-like, Iquitos-like, ruidoso, desbalanceado extremo).
- Usar como "laboratorio" para seleccionar ponderaciones robustas del Confidence Score antes de aplicar a datos reales.
- Evaluar sensibilidad a ruido y a desbalance de episodios.

### 4.3 Validación cruzada entre ciudades
- Entrenar/calibrar en San Juan → testear en Iquitos (y viceversa).
- Evaluar degradación del rendimiento y necesidad de adaptación.

### 4.4 Métricas operativas (no solo estadísticas)
- Lead-time real hasta primera acción de campo.
- Número de alertas "Alto" por año vs recursos disponibles.
- Tasa de "alertas ignoradas" que luego resultaron en brotes (falsos negativos operativos).

## 5. Plan de calibración del Confidence Score
1. Fijar thresholds de categoría (Alto/Medio/Bajo) o permitir ciudad-específicos.
2. Usar datos sintéticos para explorar grid de pesos.
3. Elegir el conjunto de pesos que maximice Brier score + F1 de "Alto" + estabilidad en regímenes difíciles (Iquitos-like).
4. Recalibrar (isotonic o Platt) sobre datos reales cuando estén disponibles.
5. Validar que la categoría "Alto" tenga alta precisión positiva en datos externos.

## 6. Riesgos y mitigaciones
- Riesgo: Seguimos con muy pocos episodios reales → mitigación: datos sintéticos + colaboración para más datos.
- Riesgo: Diferencias no modeladas entre ciudades → mitigación: modelos o thresholds adaptativos por régimen.
- Riesgo: Confusores (intervenciones vectoriales) → mitigación: incluir variables de intervención en análisis futuro.

## 7. Cronograma sugerido para Fase 9+
- Meses 1-3: Obtención y procesamiento de series extendidas PR.
- Meses 2-4: Experimentos con datos sintéticos + selección final de pesos.
- Meses 4-7: Walk-forward en datos reales + evaluación con ground-truth operativo.
- Meses 6-9: Manuscrito + piloto con equipo de vigilancia (si hay acuerdo).

---
*Protocolo generado automáticamente por fase8_external_validation_strategy.py*
