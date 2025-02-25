/*
 * Copyright (c) 2022, 2023 SAP SE. All rights reserved.
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * Please contact Oracle, 500 Oracle Parkway, Redwood Shores, CA 94065 USA
 * or visit www.oracle.com if you need additional information or have any
 * questions.
 */

/*
 * @test TestVitalsInvalidSampleInterval
 * @summary Test verifies that -XX:-EnableVitals disables vitals
 * @library /test/lib
 * @run driver TestVitalsInvalidSampleInterval run
 */

import jdk.test.lib.process.OutputAnalyzer;
import jdk.test.lib.process.ProcessTools;

public class TestVitalsInvalidSampleInterval {

    public static void main(String[] args) throws Exception {
        // Invalid Sample interval prints a warning and runs with Vitals disabled
        ProcessBuilder pb = ProcessTools.createTestJavaProcessBuilder(
                "-XX:VitalsSampleInterval=0",
                "-XX:MaxMetaspaceSize=16m",
                "-Xmx128m",
                "-version"); // Note: explicitly omit Xlog:vitals, since the warning should always appear
        OutputAnalyzer output = new OutputAnalyzer(pb.start());
        output.shouldHaveExitValue(1);
        output.shouldContain("Improperly specified VM option 'VitalsSampleInterval=0'");
    }
}
