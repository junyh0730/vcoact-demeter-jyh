#include <linux/ethtool.h>
#include <linux/netdevice.h>
#include <net/sch_generic.h>
#include <uapi/linux/ptrace.h>

#if IFNAMSIZ != 16
#error "IFNAMSIZ != 16 is not supported"
#endif
#define MAX_QUEUE_NUM 1024
#define PER_SLOT_SIZE 100

typedef struct entry_key
{
    u32 pid;
    u32 cpu;
} entry_key_t;

typedef struct irq_key
{
    u32 vec;
    u64 slot;
    u32 cpu;
} irq_key_t;

typedef struct irq_account_val
{
    u64 ts;
    u32 vec;
} irq_account_val_t;

BPF_HASH(irq_start, entry_key_t, irq_account_val_t);
BPF_HISTOGRAM(dist_irq, irq_key_t);

TRACEPOINT_PROBE(irq, softirq_entry)
{
    irq_account_val_t val = {};
    entry_key_t key = {};

    key.pid = bpf_get_current_pid_tgid();
    key.cpu = bpf_get_smp_processor_id();
    val.ts = bpf_ktime_get_ns();
    val.vec = args->vec;

    irq_start.update(&key, &val);

    return 0;
}

TRACEPOINT_PROBE(irq, softirq_exit)
{
    u64 delta;
    u32 vec;
    irq_account_val_t *valp;
    irq_key_t key = {0};
    entry_key_t entry_key = {};

    entry_key.pid = bpf_get_current_pid_tgid();
    entry_key.cpu = bpf_get_smp_processor_id();

    // fetch timestamp and calculate delta
    valp = irq_start.lookup(&entry_key);
    if (valp == 0)
    {
        return 0; // missed start
    }
    delta = (bpf_ktime_get_ns() - valp->ts);
    vec = valp->vec;

    // store as sum or histogram
    STORE

    irq_start.delete(&entry_key);
    return 0;
}