# OpenAPI 3.1 y Docstrings — Templates por stack

## Contenido
- [OpenAPI 3.1 — Node.js/Express (EfiziAI CRM)](#openapi-31--nodejsexpress-efiziai-crm)
- [.NET 8 con XML Docs (FleetVision)](#net-8-con-xml-docs-fleetvision)
- [JSDoc / TSDoc para TypeScript/Angular](#jsdoc--tsdoc-para-typescriptangular)

> Los ejemplos "EfiziAI CRM API" son ilustrativos (ese CRM está archivado).

---

## OpenAPI 3.1 — Node.js/Express (EfiziAI CRM)

```yaml
openapi: "3.1.0"
info:
  title: EfiziAI CRM API
  version: "1.0.0"
  description: |
    B2B CRM API para gestión de leads, tenants y automatizaciones.
    Todos los endpoints requieren autenticación JWT excepto /auth/*.
  contact:
    name: Cristian Gutierrez
    email: notificaciones@ejemplo.com

servers:
  - url: https://api.efiziai.com/v1
    description: Production
  - url: http://localhost:3001/v1
    description: Development

security:
  - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Lead:
      type: object
      required: [name, email, tenant_id]
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        name:
          type: string
          minLength: 2
          maxLength: 100
          example: "Empresa ABC S.A."
        email:
          type: string
          format: email
        status:
          type: string
          enum: [prospect, qualified, proposal, closed_won, closed_lost]
          default: prospect
        tenant_id:
          type: string
          format: uuid
        created_at:
          type: string
          format: date-time
          readOnly: true

    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          example: "LEAD_NOT_FOUND"
        message:
          type: string
        details:
          type: object

paths:
  /leads:
    get:
      summary: List leads
      operationId: listLeads
      tags: [Leads]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [prospect, qualified, proposal, closed_won, closed_lost]
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        "200":
          description: Paginated list of leads
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Lead"
                  total:
                    type: integer
                  page:
                    type: integer
        "401":
          $ref: "#/components/responses/Unauthorized"

    post:
      summary: Create lead
      operationId: createLead
      tags: [Leads]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Lead"
            example:
              name: "TechCorp S.A."
              email: "contacto@techcorp.com"
              tenant_id: "550e8400-e29b-41d4-a716-446655440000"
      responses:
        "201":
          description: Lead created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Lead"
        "422":
          $ref: "#/components/responses/ValidationError"
```

---

## .NET 8 con XML Docs (FleetVision)

```csharp
/// <summary>
/// Retrieves all vehicles for the current tenant.
/// </summary>
/// <param name="cancellationToken">Cancellation token.</param>
/// <returns>List of vehicles with their current status.</returns>
/// <response code="200">Returns the list of vehicles.</response>
/// <response code="401">Unauthorized — missing or invalid JWT.</response>
/// <response code="403">Forbidden — tenant mismatch.</response>
[HttpGet]
[ProducesResponseType(typeof(IEnumerable<VehicleDto>), StatusCodes.Status200OK)]
[ProducesResponseType(StatusCodes.Status401Unauthorized)]
[ProducesResponseType(StatusCodes.Status403Forbidden)]
public async Task<IActionResult> GetVehicles(CancellationToken cancellationToken)
```

---

## JSDoc / TSDoc para TypeScript/Angular

```typescript
/**
 * Fetches vehicles for the current tenant with optional filtering.
 *
 * @param filters - Optional filter criteria for the vehicle list
 * @param filters.status - Filter by vehicle status
 * @param filters.tenantId - Override tenant (admin only)
 * @returns Observable of paginated vehicle results
 *
 * @example
 * ```ts
 * this.vehicleService.getVehicles({ status: 'active' })
 *   .pipe(takeUntilDestroyed())
 *   .subscribe(result => this.vehicles.set(result.data));
 * ```
 *
 * @throws {HttpErrorResponse} 401 if JWT is expired
 * @throws {HttpErrorResponse} 403 if tenant mismatch
 */
getVehicles(filters?: VehicleFilters): Observable<PaginatedResult<Vehicle>>
```
