
import time
from videocore6.driver import Driver
from videocore6.assembler import qpu


@qpu
def qpu_clock(asm):

    nop(null, sig = 'ldunif')

    L.loop
    sub(r5, r5, 1, cond = 'pushn')
    b(R.loop, cond = 'anyna')
    nop(null)
    nop(null)
    nop(null)

    nop(null, sig = 'thrsw')
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null)


def test_clock():
    print()

    with Driver() as drv:

        f = pow(2, 25)

        code = drv.program(qpu_clock)
        unif = drv.alloc(1, dtype = 'uint32')

        unif[0] = f

        start = time.time()
        drv.execute(code, unif.addresses()[0])
        end = time.time()

        print(f'{end - start} sec')
        print(f'{f * 5 / (end - start) / 1000 / 1000 * 4} MHz')


@qpu
def qpu_tmu_write(asm):

    nop(null, sig = 'ldunif')
    bor(r1, r5, r5, sig = 'ldunif')

    # r2 = addr + eidx * 4
    # rf0 = eidx
    eidx(r0).mov(r2, r5)
    shl(r0, r0, 2).mov(rf0, r0)
    add(r2, r2, r0)

    L.loop
    if True:

        # rf0: Data to be written.
        # r0: Overwritten.
        # r2: Address to write data to.

        sub(r1, r1, 1, cond = 'pushz').mov(tmud, rf0)
        b(R.loop, cond = 'anyna')
        # rf0 += 16
        sub(rf0, rf0, -16).mov(tmua, r2)
        # r2 += 64
        shl(r0, 4, 4)
        tmuwt(null).add(r2, r2, r0)

    nop(null, sig = 'thrsw')
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null)


def test_tmu_write():
    print()

    n = 4096

    with Driver(data_area_size = n * 16 * 4 + 2 * 4) as drv:

        code = drv.program(qpu_tmu_write)
        data = drv.alloc(n * 16, dtype = 'uint32')
        unif = drv.alloc(2, dtype = 'uint32')

        data[:] = 0xdeadbeaf
        unif[0] = n
        unif[1] = data.addresses()[0]

        start = time.time()
        drv.execute(code, unif.addresses()[0])
        end = time.time()

        assert all(data == range(n * 16))


@qpu
def qpu_tmu_read(asm):

    # r0: Number of vectors to read.
    # r1: Pointer to the read vectors + eidx * 4.
    # r2: Pointer to the write vectors + eidx * 4
    eidx(r2, sig = 'ldunif')
    nop(null, sig = 'ldunif').mov(r0, r5)
    shl(r2, r2, 2).mov(r1, r5)
    add(r1, r1, r2, sig = 'ldunif')
    add(r2, r5, r2)

    L.loop
    if True:

        nop(null).mov(tmua, r1, sig = 'thrsw')
        nop(null)
        nop(null)
        nop(rf0, sig = 'ldtmu')

        sub(r0, r0, 1, cond = 'pushz').add(tmud, rf0, 1)
        b(R.loop, cond = 'anyna')
        shl(r3, 4, 4).mov(tmua, r2)
        # r1 += 64
        # r2 += 64
        add(r1, r1, r3).add(r2, r2, r3)
        tmuwt(null)

    nop(null, sig = 'thrsw')
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null, sig = 'thrsw')
    nop(null)
    nop(null)
    nop(null)


def test_tmu_read():
    print()

    n = 4096

    with Driver() as drv:

        code = drv.program(qpu_tmu_read)
        data = drv.alloc(n * 16, dtype = 'uint32')
        unif = drv.alloc(3, dtype = 'uint32')

        data[:] = range(len(data))
        unif[0] = n
        unif[1] = data.addresses()[0]
        unif[2] = data.addresses()[0]

        drv.execute(code, unif.addresses()[0])

        assert all(data == range(1, n * 16 + 1))
