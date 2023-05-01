#include "ucenv.h"

extern "C" void c_helloWorld(int); // as hello_world
extern "C" void c_init(OutputDF &, int); // as init
extern "C" void c_print(const InputDF &); // as print

// MAIN
BlockRetStatus block_0(CF &self)
{

	self.NextBlock=1;
	return CONTINUE;
}

// STRUCT: sub main()
BlockRetStatus block_1(CF &self)
{
	Id _id_0=self.create_id(); // x

// GEN BODY: sub main()
	{ // FORK_BI: cf test[1]: init(x, 128);
		CF *child=self.fork(2);
		child->id(0)=_id_0;
	}

	{ // FORK_BI: cf testPrint[1]: print(x);
		CF *child=self.fork(3);
		child->id(0)=_id_0;
	}

	{ // FORK_BI: for i=0..3;
		CF *child=self.fork(6);
		child->id(0)=_id_0;
	}

	{ // FORK_BI: for i=0..3;
		CF *child=self.fork(8);
		child->id(0)=_id_0;
	}

	return EXIT;
}

// BI_EXEC: cf test[1]: init(x, 128);
BlockRetStatus block_2(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	{
		DF _out_0;
		// EXEC_EXTERN cf test[1]: init(x, 128);
		c_init(
			// name x
			_out_0, 
			// int 128
			128);

		{
			DF stored=_out_0;
			self.store(self.id(0), stored);
		}
	}

	// req_unlimited: x
	{		DF posted=self.wait(self.id(0));
	self.post(self.id(0), posted, CyclicLocator(0), -1);
	}
	return EXIT;
}

// BI_EXEC: cf testPrint[1]: print(x);
BlockRetStatus block_3(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	// request x
	self.request(self.id(0), CyclicLocator(0));

	self.NextBlock=4;
	return CONTINUE;
}

// Request : cf testPrint[1]: print(x);
BlockRetStatus block_4(CF &self)
{
	// wait x
	if (self.wait(self.id(0)).is_unset()) {
		return WAIT;
	}


	self.NextBlock=5;
	return CONTINUE;
}

// After requests: cf testPrint[1]: print(x);
BlockRetStatus block_5(CF &self)
{
	{
		// EXEC_EXTERN cf testPrint[1]: print(x);
		c_print(
			// value x
			self.wait(self.id(0)));

	}

	return EXIT;
}

// BI_FOR: for i = 0 .. 3
BlockRetStatus block_6(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	for (int _lc_i=0; _lc_i<=3; _lc_i++) {

// GEN BODY: for i = 0 .. 3
	{ // FORK_BI: cf task1[i]: init(x[i][i], i);
		CF *child=self.fork(7);
		child->arg(0)=_lc_i;
		child->id(0)=self.id(0);
	}

	} // for
	return EXIT;
}

// BI_EXEC: cf task1[i]: init(x[i][i], i);
BlockRetStatus block_7(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	{
		DF _out_0;
		// EXEC_EXTERN cf task1[i]: init(x[i][i], i);
		c_init(
			// name x[i][i]
			_out_0, 
			// int i
			self.arg(0).get_int());

		{
			DF stored=_out_0;
			self.store(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()], stored);
		}
	}

	// req_unlimited: x[i][i]
	{		DF posted=self.wait(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()]);
	self.post(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()], posted, CyclicLocator(0), -1);
	}
	return EXIT;
}

// BI_FOR: for i = 0 .. 3
BlockRetStatus block_8(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	for (int _lc_i=0; _lc_i<=3; _lc_i++) {

// GEN BODY: for i = 0 .. 3
	{ // FORK_BI: cf task2[i]: print(x[i][i]);
		CF *child=self.fork(9);
		child->arg(0)=_lc_i;
		child->id(0)=self.id(0);
	}

	} // for
	return EXIT;
}

// BI_EXEC: cf task2[i]: print(x[i][i]);
BlockRetStatus block_9(CF &self)
{
	if (self.migrate(CyclicLocator(0))) {
		return MIGRATE;
	}

	// request x[i][i]
	self.request(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()], CyclicLocator(0));

	self.NextBlock=10;
	return CONTINUE;
}

// Request : cf task2[i]: print(x[i][i]);
BlockRetStatus block_10(CF &self)
{
	// wait x[i][i]
	if (self.wait(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()]).is_unset()) {
		return WAIT;
	}


	self.NextBlock=11;
	return CONTINUE;
}

// After requests: cf task2[i]: print(x[i][i]);
BlockRetStatus block_11(CF &self)
{
	{
		// EXEC_EXTERN cf task2[i]: print(x[i][i]);
		c_print(
			// value x[i][i]
			self.wait(self.id(0)[self.arg(0).get_int()][self.arg(0).get_int()]));

	}

	return EXIT;
}

extern "C" void init_blocks(BlocksAppender add)
{
	bool ok=true;

	ok = ok && add(block_0)==0;
	ok = ok && add(block_1)==1;
	ok = ok && add(block_2)==2;
	ok = ok && add(block_3)==3;
	ok = ok && add(block_4)==4;
	ok = ok && add(block_5)==5;
	ok = ok && add(block_6)==6;
	ok = ok && add(block_7)==7;
	ok = ok && add(block_8)==8;
	ok = ok && add(block_9)==9;
	ok = ok && add(block_10)==10;
	ok = ok && add(block_11)==11;

	assert(ok);
}

