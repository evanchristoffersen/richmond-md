program GeomRespCreator

  Implicit none

! Double precision
  integer, parameter :: kindr = kind(0d0)
! ---------------------------------------------------
! This code generate input files for
! Gaussian geometry optimization and resp calculation
! ---------------------------------------------------
  character(80) :: innamelist='namelist.in'
  character(80) :: inxyz, outgin, outrin, outgrs, outrrs
  character(20) makedirectory*40, leaper*40, remove*80, move*60, esp*40, sand*80
  character(120) anchamb
  integer, parameter :: iunamelist  = 10
  integer, parameter :: iuxyz  = 20
  integer, parameter :: iuogin  = 30
  integer, parameter :: iuorin  = 40
  integer, parameter :: iuogrs  = 50
  integer, parameter :: iuorrs  = 60
  real(kindr) :: geom(3)
  character(3) :: atom,resname
  character(80) :: confname
  integer :: jobtype,nconf,natoms,chrg,mult,i,j
  integer :: openstat,readstat
  character(80) :: string
  integer :: getcwd, status
  character(120) :: pth

! ----------------------
! open the namelist file
! ----------------------
  open(unit=iunamelist,file=innamelist,status='old',iostat=openstat)
  if (openstat /= 0) then
    write(*,'(3a)') '  Input file ',innamelist,' cannot be found '
    write(*,'(a)') '  aborting ...... '
    stop
  end if
  read(iunamelist,*,iostat=readstat)
  read(iunamelist,*,iostat=readstat) jobtype
  read(iunamelist,*,iostat=readstat)
  read(iunamelist,*,iostat=readstat) nconf
  read(iunamelist,*,iostat=readstat)
  read(iunamelist,*,iostat=readstat) natoms
  read(iunamelist,*,iostat=readstat)
  read(iunamelist,*,iostat=readstat) chrg,mult
  read(iunamelist,*,iostat=readstat)
  read(iunamelist,*,iostat=readstat) resname
  read(iunamelist,*,iostat=readstat)
  do i=1,nconf
    read(iunamelist,*,iostat=readstat) confname
    !------------------------------------------
    ! Creating Gaussian inputs and running them
    !------------------------------------------
    if (jobtype == 1) then
      inxyz = trim(confname) // '.xyz'
      open(unit=iuxyz,file=inxyz,status='old',iostat=openstat)
      if (openstat /= 0) then
        write(*,'(3a)') '  Input file ',inxyz,' cannot be found '
        write(*,'(a)') '  aborting ...... '
        stop
      end if
      read(iuxyz,*,iostat=readstat)
      read(iuxyz,*,iostat=readstat)
      !--------------------------------------------
      ! Create Gaussian geometry optimization input
      !--------------------------------------------
      outgin = trim(confname) // '_geom.inp'
      open(unit=iuogin,file=outgin,status='new',iostat=openstat)
      write(iuogin,'(a)') '%NProcShared=12'
      write(iuogin,'(a)') '%mem=12GB'
      write(iuogin,'(3a)') '%rwf=/tmp/',trim(confname),',-1'
      write(iuogin,'(5a)') '%chk=/tmp/',trim(confname),'/',trim(confname),'_geom.chk'
      write(iuogin,'(a)') '#P HF/6-31g* OPT(Tight) scf(tight)'
      write(iuogin,'(a)') ''
      write(iuogin,'(a)') 'Gaussian09 geometry optimization (using HF/6-31G*)'
      write(iuogin,'(a)') ''
      write(iuogin,'(2I3)') chrg,mult 
      do j=1,natoms
        read(iuxyz,*,iostat=readstat) string,geom(1),geom(2),geom(3)
        write(iuogin,'(a3,3f11.5)') string,geom(1),geom(2),geom(3)
      end do
      write(iuogin,'(a)') ''
      close(iuogin)
      close(iuxyz)
      !---------------------------------------
      ! Create Gaussian RESP calculation input
      !---------------------------------------
      outrin = trim(confname) // '_resp.inp'
      open(unit=iuorin,file=outrin,status='new',iostat=openstat)
      write(iuorin,'(a)') '%NProcShared=12'
      write(iuorin,'(a)') '%mem=12GB'
      write(iuorin,'(3a)') '%rwf=/tmp/',trim(confname),',-1'
      write(iuorin,'(5a)') '%chk=/tmp/',trim(confname),'/',trim(confname),'_resp.chk'
      write(iuorin,'(a)') '#P B3LYP/cc-pVTZ  SCF=Tight  Pop=MK IOp(6/33=2,6/41=10,6/42=17)'
      write(iuorin,'(a)') ''
      write(iuorin,'(a)') 'Gaussian09 single point electrostatic potental calc (using B3LYP/cc-pVTZ)'
      write(iuorin,'(a)') ''
      write(iuorin,'(2I3)') chrg,mult
      write(iuogin,'(a)') ''
      close(iuorin)
      !------------------------------
      ! Get current working directory
      !------------------------------
      status = getcwd( pth )
      if ( status .ne. 0 ) stop 'getcwd: error'
  
      pth = pth(1:120)
  
      !-----------------------
      ! Create geom run script
      !-----------------------
      outgrs = 'g09_geom.pbs'
      open(unit=iuogrs,file=outgrs,status='new',iostat=openstat)
      write(iuogrs,'(a)') '#!/bin/bash'
      write(iuogrs,'(a)') '## Enter name of job here:'
      write(iuogrs,'(3a)') '#SBATCH --output=',trim(confname),'_geom'
      write(iuogrs,'(a)') '## Enter queue here:'
      write(iuogrs,'(a)') '#SBATCH --partition=short'
      write(iuogrs,'(a)') '## Enter number of nodes and processors to use here:'
      write(iuogrs,'(a)') '#SBATCH --nodes=1'
!      write(iuogrs,'(a)') '## Enter your working directory here:'
!      write(iuogrs,'(a)') '#PBS -d ',trim(adjustl(pth)),'/',trim(confname)
      write(iuogrs,'(a)') '## Enter number of tasks-per-nodes here:'
      write(iuogrs,'(a)') '#SBATCH --ntasks-per-node=8'
      write(iuogrs,'(a)') '## Enter export option here:'
      write(iuogrs,'(a)') '#SBATCH --export=ALL'
      write(iuogrs,'(a)') '## Enter run time here:'
      write(iuogrs,'(a)') '#SBATCH --time=0-24:00:00'
      write(iuogrs,'(a)') '## Enter name of batch error and/or output here:'
      write(iuogrs,'(3a)') '#SBATCH --error=',trim(confname),'_geom.err'
!      write(iuogrs,'(a)') '## This joins batch error and output:'
!      write(iuogrs,'(a)') '#PBS -j oe'
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(a)') 'hostname'
      write(iuogrs,'(a)') ''
      write(iuogrs,'(a)') '# Create scratch directory here:'
      write(iuogrs,'(4a)') 'test -d /tmp/',trim(confname),' || mkdir -v /tmp/',trim(confname)
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(a)') '# Activate Gaussian:'
      write(iuogrs,'(a)') '#export g09root=/usr/local/packages/gaussian'
      write(iuogrs,'(a)') '#. $g09root/g09/bsd/g09.profile'
      write(iuogrs,'(a)') 'module load gaussian'
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(a)') 'which g09'
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(5a)') 'g09 < ',trim(confname),'_geom.inp > ',trim(confname),'_geom.out'
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(a)') '# Copy checkpoint file from local scratch to working directory after job completes:'
      write(iuogrs,'(5a)') 'cp -pv /tmp/',trim(confname),'/',trim(confname),'_geom.chk .'
      write(iuogrs,'(a)') ' '
      write(iuogrs,'(a)') '# Clean up scratch:'
      write(iuogrs,'(2a)') 'rm -rv /tmp/',trim(confname)
      write(iuogrs,'(a)') ' '
  
      close(iuogrs)
  
      !-----------------------
      ! Create resp run script
      !-----------------------
      outrrs = 'g09_resp.pbs'
      open(unit=iuorrs,file=outrrs,status='new',iostat=openstat)
      write(iuorrs,'(a)') '#!/bin/bash'
      write(iuorrs,'(a)') '## Enter name of job here:'
      write(iuorrs,'(3a)') '#SBATCH --output=',trim(confname),'_resp'
      write(iuorrs,'(a)') '## Enter queue here:'
      write(iuorrs,'(a)') '#SBATCH --partition=short'
      write(iuorrs,'(a)') '## Enter number of nodes and processors to use here:'
      write(iuorrs,'(a)') '#SBATCH --nodes=1'     
!      write(iuorrs,'(a)') '## Enter your working directory here:'
!      write(iuorrs,'(a)') '#PBS -d ',trim(adjustl(pth)),'/',trim(confname)
      write(iuorrs,'(a)') '## Enter number of tasks-per-nodes here:'
      write(iuorrs,'(a)') '#SBATCH --ntasks-per-node=8'
      write(iuorrs,'(a)') '## Enter export option here:'
      write(iuorrs,'(a)') '#SBATCH --export=ALL'
      write(iuorrs,'(a)') '## Enter run time here:'
      write(iuorrs,'(a)') '#SBATCH --time=0-24:00:00'     
      write(iuorrs,'(a)') '## Enter name of batch error and/or output here:'
      write(iuorrs,'(3a)') '#SBATCH --error=',trim(confname),'_resp.err'
!      write(iuorrs,'(a)') '## This joins batch error and output:'
!      write(iuorrs,'(a)') '#PBS -j oe'
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(a)') 'hostname'
      write(iuorrs,'(a)') ''
      write(iuorrs,'(a)') '# Create scratch directory here:'
      write(iuorrs,'(4a)') 'test -d /tmp/',trim(confname),' || mkdir -v /tmp/',trim(confname)
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(a)') '# Activate Gaussian:'
      write(iuorrs,'(a)') '#export g09root=/usr/local/packages/gaussian'
      write(iuorrs,'(a)') '#. $g09root/g09/bsd/g09.profile'
      write(iuorrs,'(a)') 'module load gaussian'
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(a)') 'which g09'
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(5a)') 'g09 < ',trim(confname),'_resp.inp > ',trim(confname),'_resp.out'
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(a)') '# Copy checkpoint file from local scratch to working directory after job completes:'
      write(iuorrs,'(5a)') 'cp -pv /tmp/',trim(confname),'/',trim(confname),'_resp.chk .'
      write(iuorrs,'(a)') ' '
      write(iuorrs,'(a)') '# Clean up scratch:'
      write(iuorrs,'(2a)') 'rm -rv /tmp/',trim(confname)
      write(iuorrs,'(a)') ' '
  
      close(iuorrs)
  
      makedirectory = 'mkdir ' // trim(confname)
      print*, makedirectory
      call system(makedirectory)
  
      move = 'mv '//trim(confname)//'_geom.inp '//trim(confname)//'/.'
      print*,move
      call system(move)
  
      move = 'mv '//trim(confname)//'_resp.inp '//trim(confname)//'/.'
      print*,move
      call system(move)
  
      move = 'mv g09_geom.pbs '//trim(confname)//'/.'
      print*,move
      call system(move)
  
      move = 'mv g09_resp.pbs '//trim(confname)//'/.'
      print*,move
      call system(move)

      call system('cd '//trim(confname)//'/ && sbatch -A richmondlab g09_geom.pbs ')

    end if
    !-------------------------------------------
    ! Getting esp.dat from Gaussian RESP outputs
    !-------------------------------------------
    if (jobtype == 2) then
     
      esp = './esp.sh '//trim(confname)//'_resp.out'
      print*,esp
      call system(esp)

      move = 'mv esp.dat '//trim(confname)//'_esp.dat '
      print*,move
      call system(move)

    end if
    !----------------------------------------------------------------
    ! Running antechamber and LEAP and sander with default atom types
    !----------------------------------------------------------------
    if (jobtype == 3 .OR. jobtype == 4) then

      move = 'mv '//trim(confname)//'_esp.dat esp.dat'
      print*,move
      call system(move)
   
      if (jobtype == 3) then
        anchamb = 'antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -at amber -fi mol2 -i '&
//trim(confname)//'.mol2 -rn '//trim(resname)
        print*,anchamb
        call system(anchamb)
      end if

      if (jobtype == 4) then
        anchamb = 'antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -fi mol2 -i '&
//trim(confname)//'.mol2 -rn '//trim(resname)//' -fa mol2 -ao type -a '&
//trim(confname)//'.mol2 '
        print*,anchamb
        call system(anchamb)
      end if

      leaper = 'tleap -s -f leap.in'
      print*,leaper
      call system(leaper)

      sand = 'sander -O -i sander.in -o sander.out -c prmcrd -p prmtop'
      print*,sand
      call system(sand)

      remove = 'rm ANTECHAMBER* ATOMTYPE.INF leap.log mdinfo prmcrd sander.out restrt '
      print*,remove
      call system(remove)

      move = 'mv Temp.mol2 '//trim(confname)//'.mol2'
      print*,move
      call system(move)

      move = 'mv esp.dat '//trim(confname)//'_esp.dat'
      print*,move
      call system(move)

      move = 'mv prmtop '//trim(confname)//'.top'
      print*,move
      call system(move)

      move = 'mv esp.induced '//trim(confname)//'_esp.induced'
      print*,move
      call system(move)

      move = 'mv esp.qm-induced '//trim(confname)//'_esp.qm-induced'
      print*,move
      call system(move)

    end if



  end do


end program GeomRespCreator

