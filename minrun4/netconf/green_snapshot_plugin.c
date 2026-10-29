#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <libyang/libyang.h>
#include <sysrepo.h>

typedef struct {
    char *snapshot_path;
    sr_subscription_ctx_t *hardware_subscription;
    sr_subscription_ctx_t *energy_subscription;
} green_plugin_state_t;

static char *
read_snapshot(const char *path)
{
    FILE *file = NULL;
    char *buffer = NULL;
    long length;
    size_t read_length;

    file = fopen(path, "rb");
    if (!file) {
        return NULL;
    }
    if (fseek(file, 0, SEEK_END) != 0 || (length = ftell(file)) < 0 ||
            fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return NULL;
    }

    buffer = malloc((size_t)length + 1);
    if (!buffer) {
        fclose(file);
        return NULL;
    }
    read_length = fread(buffer, 1, (size_t)length, file);
    fclose(file);
    if (read_length != (size_t)length) {
        free(buffer);
        return NULL;
    }
    buffer[read_length] = '\0';
    return buffer;
}

static int
provide_operational_data(sr_session_ctx_t *session, uint32_t subscription_id,
        const char *module_name, const char *path, const char *request_xpath,
        uint32_t request_id, struct lyd_node **parent, void *private_data)
{
    green_plugin_state_t *state = private_data;
    const char *schema_path;
    const struct ly_ctx *ly_ctx;
    char *json;
    struct lyd_node *data = NULL;
    struct lyd_node *source = NULL;
    struct lyd_node *copy = NULL;
    LY_ERR ly_result;
    int result = SR_ERR_OK;

    (void)subscription_id;
    (void)request_xpath;
    (void)request_id;

    if (!strcmp(module_name, "ietf-hardware") && !strcmp(path, "/ietf-hardware:hardware")) {
        schema_path = "/ietf-hardware:hardware";
    } else if (!strcmp(module_name, "ietf-power-and-energy") &&
            !strcmp(path, "/ietf-power-and-energy:energy-objects")) {
        schema_path = "/ietf-power-and-energy:energy-objects";
    } else {
        return SR_ERR_OK;
    }

    json = read_snapshot(state->snapshot_path);
    if (!json) {
        if (errno == ENOENT) {
            return SR_ERR_OK;
        }
        fprintf(stderr, "green-snapshot-plugin: cannot read %s\n", state->snapshot_path);
        return SR_ERR_SYS;
    }

    ly_ctx = sr_get_context(sr_session_get_connection(session));
    ly_result = lyd_parse_data_mem(ly_ctx, json, LYD_JSON, LYD_PARSE_STRICT,
            LYD_VALIDATE_PRESENT, &data);
    free(json);
    if (ly_result != LY_SUCCESS) {
        fprintf(stderr, "green-snapshot-plugin: failed to parse operational snapshot\n");
        return SR_ERR_VALIDATION_FAILED;
    }

    ly_result = lyd_find_path(data, schema_path, 0, &source);
    if (ly_result == LY_SUCCESS && source) {
        ly_result = lyd_dup_single(source, NULL, LYD_DUP_RECURSIVE, &copy);
        if (ly_result == LY_SUCCESS) {
            if (*parent) {
                ly_result = lyd_insert_child(*parent, copy);
            } else {
                *parent = copy;
            }
        }
    } else if (ly_result == LY_ENOTFOUND) {
        ly_result = LY_SUCCESS;
    }

    lyd_free_all(data);
    if (ly_result != LY_SUCCESS) {
        fprintf(stderr, "green-snapshot-plugin: failed to provide %s\n", schema_path);
        result = SR_ERR_OPERATION_FAILED;
    }
    return result;
}

int
sr_plugin_init_cb(sr_session_ctx_t *session, void **private_data)
{
    green_plugin_state_t *state;
    const char *snapshot_path = getenv("GREEN_NETCONF_STATE_FILE");
    int result;

    if (!snapshot_path || !snapshot_path[0]) {
        fprintf(stderr, "green-snapshot-plugin: GREEN_NETCONF_STATE_FILE is required\n");
        return SR_ERR_INVAL_ARG;
    }

    state = calloc(1, sizeof *state);
    if (!state) {
        return SR_ERR_NO_MEMORY;
    }
    state->snapshot_path = strdup(snapshot_path);
    if (!state->snapshot_path) {
        free(state);
        return SR_ERR_NO_MEMORY;
    }

    result = sr_oper_get_items_subscribe(session, "ietf-hardware", "/ietf-hardware:hardware",
            provide_operational_data, state, 0, &state->hardware_subscription);
    if (result != SR_ERR_OK) {
        free(state->snapshot_path);
        free(state);
        return result;
    }

    result = sr_oper_get_items_subscribe(session, "ietf-power-and-energy",
            "/ietf-power-and-energy:energy-objects", provide_operational_data,
            state, 0, &state->energy_subscription);
    if (result != SR_ERR_OK) {
        sr_unsubscribe(state->hardware_subscription);
        free(state->snapshot_path);
        free(state);
        return result;
    }

    *private_data = state;
    return SR_ERR_OK;
}

void
sr_plugin_cleanup_cb(sr_session_ctx_t *session, void *private_data)
{
    green_plugin_state_t *state = private_data;
    (void)session;

    if (!state) {
        return;
    }
    if (state->hardware_subscription) {
        sr_unsubscribe(state->hardware_subscription);
    }
    if (state->energy_subscription) {
        sr_unsubscribe(state->energy_subscription);
    }
    free(state->snapshot_path);
    free(state);
}
