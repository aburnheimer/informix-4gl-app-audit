.PHONY: cleantestmod testmod
.PRECIOUS: %.4gm

%.4gm:
	mkdir -p $@

%.4gs: audittest.4gm
	mkdir audittest.4gm/$@
	# Create plaintext files
	@for e in org ext 4gl; do \
		printf "Creating *$$e files\n"; \
		for f in bko_hold.$$e bko_stubs.$$e dummy.$$e globals.$$e main.$$e rel_chrg.$$e tmp_main.$$e; do \
			echo "-- random-id: $$(date +%s)\n\nMAIN\n\tDISPLAY \"Hello from $$f\"\nEND MAIN\n" > audittest.4gm/$@/$$f; \
		done; \
	done

	@printf "Creating misc files\n"
	@echo "bko_hold\nbko_stubs\ndummy\nglobals\nmain\nrel_chrg\ntmp_main" > audittest.4gm/$@/base.set

	@# XXX Need to make this filelist.RDS more accurate; consider generating it dynamically based on actual files
	@echo "bko_hold\nbko_stubs\ndummy\nglobals\nmain\nrel_chrg\ntmp_main" > audittest.4gm/$@/filelist.RDS

	@echo ".PHONY: dummytask\n\ndummytask:\n\techo \"Hello Makefile\"" > audittest.4gm/$@/Makefile;

	# Create binary files
	@seed=$$RANDOM; \
		size=$$(awk -v s="$$seed" 'BEGIN{srand(s); print int(rand()*1024)+3073}'); \
		gi_file=$$(echo "$@" | sed 's/\.4gs$$/.4gi/'); \
		printf "Creating $$gi_file (%s bytes)\n" "$$size"; \
		dd if=/dev/urandom bs=1 count=$$size 2>/dev/null > audittest.4gm/$@/$$gi_file; \

	@for f in bko_hold.4go bko_stubs.4go dummy.4go globals.4go main.4go rel_chrg.4go tmp_main.4go; do \
		seed=$$RANDOM; \
			size=$$(awk -v s="$$seed" 'BEGIN{srand(s); print int(rand()*512)+513}'); \
			printf "Creating $$f (%s bytes)\n" "$$size"; \
			dd if=/dev/urandom bs=1 count=$$size 2>/dev/null > audittest.4gm/$@/$$f; \
	done;

testmod: i_orders.4gs i_retrec.4gs i_rlsaut.4gs o_brzvrf.4gs

cleantestmod:
	rm -rf audittest.4gm