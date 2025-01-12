# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Chai(CMakePackage, CudaPackage, ROCmPackage):
    """
    Copy-hiding array interface for data migration between memory spaces
    """

    homepage = "https://github.com/LLNL/CHAI"
    git      = "https://github.com/LLNL/CHAI.git"

    maintainers = ['davidbeckingsale']

    version('develop', branch='develop', submodules=True)
    version('main', branch='main', submodules=True)
    version('2.4.0', tag='v2.4.0', submodules=True)
    version('2.3.0', tag='v2.3.0', submodules=True)
    version('2.2.2', tag='v2.2.2', submodules=True)
    version('2.2.1', tag='v2.2.1', submodules=True)
    version('2.2.0', tag='v2.2.0', submodules=True)
    version('2.1.1', tag='v2.1.1', submodules=True)
    version('2.1.0', tag='v2.1.0', submodules=True)
    version('2.0.0', tag='v2.0.0', submodules=True)
    version('1.2.0', tag='v1.2.0', submodules=True)
    version('1.1.0', tag='v1.1.0', submodules=True)
    version('1.0', tag='v1.0', submodules=True)

    variant('enable_pick', default=False, description='Enable pick method')
    variant('shared', default=True, description='Build Shared Libs')
    variant('raja', default=False, description='Build plugin for RAJA')
    variant('benchmarks', default=False, description='Build benchmarks.')
    variant('examples', default=True, description='Build examples.')
    variant('openmp', default=False, description='Build using OpenMP')
    # TODO: figure out gtest dependency and then set this default True
    # and remove the +tests conflict below.
    variant('tests', default=False, description='Build tests')

    depends_on('cmake@3.8:', type='build')
    depends_on('cmake@3.9:', type='build', when="+cuda")

    depends_on('blt@0.4.1:', type='build', when='@2.4.0:')
    depends_on('blt@0.4.0:', type='build', when='@2.3.0')
    depends_on('blt@0.3.6:', type='build', when='@:2.2.2')

    depends_on('umpire')
    depends_on('umpire@6.0.0', when="@2.4.0")
    depends_on('umpire@4.1.2', when="@2.2.0:2.3.0")
    depends_on('umpire@main', when='@main')

    with when('+cuda'):
        depends_on('umpire+cuda')
        for sm_ in CudaPackage.cuda_arch_values:
            depends_on('umpire+cuda cuda_arch={0}'.format(sm_),
                       when='cuda_arch={0}'.format(sm_))

    with when('+rocm'):
        depends_on('umpire+rocm')
        for arch in ROCmPackage.amdgpu_targets:
            depends_on('umpire+rocm amdgpu_target={0}'.format(arch),
                       when='amdgpu_target={0}'.format(arch))

    with when('+raja'):
        depends_on('raja~openmp', when='~openmp')
        depends_on('raja+openmp', when='+openmp')
        depends_on('raja@0.14.0', when="@2.4.0")
        depends_on('raja@0.13.0', when="@2.3.0")
        depends_on('raja@0.12.0', when="@2.2.0:2.2.2")
        depends_on('raja@main', when='@main')

        with when('+cuda'):
            depends_on('raja+cuda')
            for sm_ in CudaPackage.cuda_arch_values:
                depends_on('raja+cuda cuda_arch={0}'.format(sm_),
                           when='cuda_arch={0}'.format(sm_))
        with when('+rocm'):
            depends_on('raja+rocm')
            for arch in ROCmPackage.amdgpu_targets:
                depends_on('raja+rocm amdgpu_target={0}'.format(arch),
                           when='amdgpu_target={0}'.format(arch))

    conflicts('+benchmarks', when='~tests')

    def cmake_args(self):
        spec = self.spec

        options = []
        options.append('-DBLT_SOURCE_DIR={0}'.format(spec['blt'].prefix))

        options.append(self.define_from_variant('ENABLE_OPENMP', 'openmp'))

        if '+cuda' in spec:
            options.extend([
                '-DENABLE_CUDA=ON',
                '-DCMAKE_CUDA_SEPARABLE_COMPILATION=On',
                '-DCUDA_SEPARABLE_COMPILATION=On',
                '-DCUDA_TOOLKIT_ROOT_DIR=' + spec['cuda'].prefix])

            if not spec.satisfies('cuda_arch=none'):
                cuda_arch = spec.variants['cuda_arch'].value
                options.append('-DCUDA_ARCH=sm_{0}'.format(cuda_arch[0]))
                flag = '-arch sm_{0}'.format(cuda_arch[0])
                options.append('-DCMAKE_CUDA_FLAGS:STRING={0}'.format(flag))
        else:
            options.append('-DENABLE_CUDA=OFF')

        if '+rocm' in spec:
            options.extend([
                '-DENABLE_HIP=ON',
                '-DHIP_ROOT_DIR={0}'.format(spec['hip'].prefix)
            ])
            archs = self.spec.variants['amdgpu_target'].value
            if archs != 'none':
                arch_str = ",".join(archs)
                options.append(
                    '-DHIP_HIPCC_FLAGS=--amdgpu-target={0}'.format(arch_str)
                )
        else:
            options.append('-DENABLE_HIP=OFF')

        if '+raja' in spec:
            options.extend(['-DENABLE_RAJA_PLUGIN=ON',
                            '-DRAJA_DIR=' + spec['raja'].prefix])

        options.append(self.define_from_variant('ENABLE_PICK', 'enable_pick'))

        options.append('-Dumpire_DIR:PATH='
                       + spec['umpire'].prefix.share.umpire.cmake)

        options.append('-DENABLE_TESTS={0}'.format(
            'ON' if '+tests' in spec  else 'OFF'))

        options.append(self.define_from_variant('ENABLE_BENCHMARKS', 'benchmarks'))

        options.append(self.define_from_variant('ENABLE_EXAMPLES', 'examples'))

        options.append('-DENABLE_BENCHMARKS={0}'.format(
            'ON' if '+benchmarks' in spec else 'OFF'))

        return options
