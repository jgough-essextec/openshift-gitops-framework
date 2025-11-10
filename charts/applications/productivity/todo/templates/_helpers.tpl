{{/*
Expand the name of the chart.
*/}}
{{- define "todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo.labels" -}}
helm.sh/chart: {{ include "todo.chart" . }}
{{ include "todo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo.backend.labels" -}}
{{ include "todo.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo.backend.selectorLabels" -}}
{{ include "todo.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo.frontend.labels" -}}
{{ include "todo.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo.frontend.selectorLabels" -}}
{{ include "todo.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate route host
*/}}
{{- define "todo.routeHost" -}}
{{- if .Values.route.host }}
{{- .Values.route.host }}
{{- else if and .Values.cluster.cluster .Values.cluster.cluster.name .Values.cluster.cluster.top_level_domain }}
{{- printf "todo.apps.%s.%s" .Values.cluster.cluster.name .Values.cluster.cluster.top_level_domain }}
{{- else }}
{{- printf "todo.apps.%s" (.Release.Namespace | default "todo") }}
{{- end }}
{{- end }}
